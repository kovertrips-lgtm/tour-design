
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas, Scrollbar, Frame, Label, Button, Toplevel
import logging

# --- LOGGING SETUP ---
log_file = os.path.join(os.path.expanduser("~"), "Documents", "kover_debug.log")
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log(msg):
    print(msg)
    logging.info(msg)

try:
    from PIL import Image, ImageTk, ImageOps
except ImportError as e:
    log(f"PIL Error: {e}")

# --- CONFIG ---
THUMB_SIZE = (200, 200)
BG_COLOR = "#1e1e1e"
SIDEBAR_COLOR = "#252526"
# TEXT_COLOR = "#E0E0E0" 

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".kover_cache")
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class PhotoCullApp:
    def __init__(self, root):
        log("Initializing App...")
        self.root = root
        self.root.title("Kover Photo Cull")
        self.root.geometry("1000x700")
        
        # Force a theme that is usually visible
        style = ttk.Style()
        try:
            style.theme_use('aqua') # Native Mac
        except:
            style.theme_use('default')
            
        # Configure Treeview colors explicitly for Dark Mode issues
        # Text needs to be visible on dark sidebar
        style.configure("Treeview", 
                        background="white", 
                        foreground="black", 
                        fieldbackground="white",
                        font=("Helvetica", 12))
        
        self.all_files = []
        self.selection = []
        self.photo_cache = {}
        self.thumb_queue = []
        self.current_folder = ""
        self.running = True

        # Layout
        main_splits = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_splits.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = Frame(main_splits, width=250, bg="#dddddd")
        self.sidebar.pack_propagate(False)
        main_splits.add(self.sidebar)
        
        # Tree
        lbl = Label(self.sidebar, text="Folders", bg="#dddddd", font=("Arial", 14, "bold"))
        lbl.pack(pady=5)
        
        self.tree = ttk.Treeview(self.sidebar)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree.bind('<<TreeviewOpen>>', self._on_tree_open)
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        
        # Bottom sidebar
        btn_debug = Button(self.sidebar, text="Check Logs", command=self.show_debug)
        btn_debug.pack(pady=5)
        
        self.lbl_count = Label(self.sidebar, text="0 Selected", font=("Arial", 16))
        self.lbl_count.pack(pady=5)
        
        Button(self.sidebar, text="Review & Upload", command=self.open_review).pack(fill=tk.X, padx=5, pady=5)

        # Content
        self.content = Frame(main_splits, bg="#333")
        main_splits.add(self.content)
        
        self.path_lbl = Label(self.content, text="Ready", bg="#333", fg="white")
        self.path_lbl.pack(fill=tk.X, pady=5)
        
        # Canvas
        self.canvas = Canvas(self.content, bg="#333", highlightthickness=0)
        sb = Scrollbar(self.content, command=self.canvas.yview)
        
        self.grid_frame = Frame(self.canvas, bg="#333")
        self.win_id = self.canvas.create_window((0,0), window=self.grid_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=sb.set)
        
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind_all("<MouseWheel>", self._on_scroll)
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Init Roots
        self.populate_roots()
        
        # Worker
        threading.Thread(target=self.worker, daemon=True).start()
        log("App Ready")

    def populate_roots(self):
        log("Populating roots...")
        # 1. Volumes
        try:
            if os.path.exists("/Volumes"):
                node = self.tree.insert("", "end", text="/Volumes", values=["/Volumes"], open=False)
                self.tree.insert(node, "end", text="dummy")
                log("Added /Volumes")
        except Exception as e:
            log(f"Error adding volumes: {e}")

        # 2. User Home
        try:
            home = os.path.expanduser("~")
            node = self.tree.insert("", "end", text="Home", values=[home], open=True) # Open by default
            self.populate_node(node, home)
            log(f"Added Home: {home}")
        except Exception as e:
            log(f"Error adding home: {e}")
            
    def populate_node(self, parent, path):
        # Clear
        self.tree.delete(*self.tree.get_children(parent))
        
        try:
            items = os.listdir(path)
            items.sort()
            count = 0
            for x in items:
                if x.startswith('.'): continue
                full = os.path.join(path, x)
                if os.path.isdir(full):
                    oid = self.tree.insert(parent, "end", text=x, values=[full])
                    self.tree.insert(oid, "end", text="dummy") # Lazy load
                    count += 1
            log(f"Populated {path} with {count} items")
        except PermissionError:
            log(f"Permission denied: {path}")
        except Exception as e:
            log(f"Error reading {path}: {e}")

    def _on_tree_open(self, e):
        sel = self.tree.selection()
        if not sel: return
        
        # Check dummy
        children = self.tree.get_children(sel[0])
        if len(children) == 1 and self.tree.item(children[0], 'text') == "dummy":
            vals = self.tree.item(sel[0], 'values')
            if vals:
                self.populate_node(sel[0], vals[0])

    def _on_tree_select(self, e):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], 'values')
        if vals:
            self.load_images(vals[0])

    def load_images(self, path):
        log(f"Loading images from {path}")
        self.current_folder = path
        self.path_lbl.config(text=path)
        
        for w in self.grid_frame.winfo_children(): w.destroy()
        self.thumb_queue = []
        self.all_files = []
        
        try:
            files = os.listdir(path)
            files = [f for f in files if f.lower().endswith(('.jpg','.png','.jpeg','.webp','.heic'))]
            files.sort()
            self.all_files = [os.path.join(path, f) for f in files]
            
            self.render_grid()
        except Exception as e:
            log(f"Error listing images: {e}")

    def render_grid(self):
        w = self.root.winfo_width() - 280
        if w < 200: w = 600
        cols = max(3, w // 210)
        
        for i, fp in enumerate(self.all_files):
            r, c = divmod(i, cols)
            f = Frame(self.grid_frame, width=200, height=200, bg="#444")
            f.grid(row=r, column=c, padx=5, pady=5)
            f.pack_propagate(False)
            
            l = Label(f, text="...", bg="#555", fg="white")
            l.pack(fill=tk.BOTH, expand=True)
            
            if fp in self.selection:
                f.config(bg="green")
            
            # Bind
            l.bind("<Button-1>", lambda e, p=fp, w=f: self.toggle(p, w))
            
            self.thumb_queue.append((fp, l))

    def toggle(self, path, widget):
        if path in self.selection:
            self.selection.remove(path)
            widget.config(bg="#444")
        else:
            self.selection.append(path)
            widget.config(bg="green")
        self.lbl_count.config(text=f"{len(self.selection)} Selected")

    def worker(self):
        while self.running:
            if not self.thumb_queue: 
                import time
                time.sleep(0.1)
                continue
            
            path, lbl = self.thumb_queue.pop(0)
            try:
                if not lbl.winfo_exists(): continue
                
                # Check cache
                if path in self.photo_cache:
                    img = self.photo_cache[path]
                else:
                    pil_img = Image.open(path)
                    pil_img.thumbnail((190, 190))
                    img = ImageTk.PhotoImage(pil_img)
                    self.photo_cache[path] = img
                
                self.root.after(0, lambda l=lbl, i=img: l.config(image=i, text=""))
            except Exception as e:
                pass # Fail silently

    def _on_scroll(self, e):
        self.canvas.yview_scroll(int(-1*e.delta), "units")

    def show_debug(self):
        try:
            with open(log_file, 'r') as f:
                txt = f.read()
            win = Toplevel(self.root)
            t = tk.Text(win)
            t.pack()
            t.insert("1.0", txt)
        except:
            pass

    def open_review(self):
        if not self.selection: return
        ReviewWindow(self.root, self.selection, self.finish)

    def finish(self, sel):
        self.selection = sel
        self.lbl_count.config(text=f"{len(sel)} Selected")
        self.render_grid()

class ReviewWindow:
    def __init__(self, parent, selection, cb):
        self.selection = selection[:]
        self.cb = cb
        self.win = Toplevel(parent)
        self.win.geometry("800x600")
        
        # Simple upload logic here if needed reused from before...
        # Just stub for now to confirm visibility
        Label(self.win, text="Review Window").pack()
        
        btn = Button(self.win, text="Simulate Upload", command=self.up)
        btn.pack()

    def up(self):
        messagebox.showinfo("Info", f"Upload {len(self.selection)} items")
        self.win.destroy()
        self.cb(self.selection)

if __name__ == "__main__":
    t = tk.Tk()
    app = PhotoCullApp(t)
    t.mainloop()
