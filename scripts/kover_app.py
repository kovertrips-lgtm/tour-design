
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas, Scrollbar, Frame, Label, Button, Toplevel

from PIL import Image, ImageTk, ImageOps

# --- CONFIG ---
THUMB_SIZE = (200, 200)
# Use safer colors for macOS dark mode compatibility
BG_COLOR = "#1e1e1e"
SIDEBAR_COLOR = "#2C2C2E" 
CARD_COLOR = "#3A3A3C"
SEL_COLOR = "#30D158" # Green
TEXT_COLOR = "#FFFFFF"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".kover_cache")

# Ensure cache dir
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class PhotoCullApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kover Photo Cull")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_COLOR)

        # State
        self.current_folder = ""
        self.all_files = [] 
        self.selection = [] 
        self.photo_cache = {} 
        self.thumb_queue = []
        self.running = True
        
        # --- STYLES ---
        # On macOS, sometimes themes glitch. Let's try 'default' with specific color overrides.
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure("Treeview", 
                        background=SIDEBAR_COLOR, 
                        foreground="#FFFFFF", 
                        fieldbackground=SIDEBAR_COLOR,
                        borderwidth=0,
                        rowheight=25,
                        font=("Helvetica", 13))
        
        style.map('Treeview', 
                  background=[('selected', '#0A84FF')], 
                  foreground=[('selected', 'white')])
        
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) # Remove borders

        # --- LAYOUT ---
        # Main Container
        self.container = Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill=tk.BOTH, expand=True)

        # PanedWindow
        self.paned = tk.PanedWindow(self.container, orient=tk.HORIZONTAL, bg="#000000", sashwidth=2, sashrelief=tk.FLAT)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 1. Sidebar Frame
        self.sidebar = Frame(self.paned, bg=SIDEBAR_COLOR, width=280)
        self.sidebar.pack_propagate(False) # Force width
        
        # 2. Main content Frame
        self.main_area = Frame(self.paned, bg=BG_COLOR)
        
        self.paned.add(self.sidebar)
        self.paned.add(self.main_area)

        # --- SIDEBAR CONTENT ---
        # Brand
        lbl_title = Label(self.sidebar, text="KoverCull", bg=SIDEBAR_COLOR, fg="#FFFFFF", font=("Helvetica", 18, "bold"))
        lbl_title.pack(pady=(20, 10), padx=15, anchor="w")

        # Treeview Container
        tree_frame = Frame(self.sidebar, bg=SIDEBAR_COLOR)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        sb = Scrollbar(tree_frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, yscrollcommand=sb.set, show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.tree.yview)

        # Bindings
        self.tree.bind('<<TreeviewOpen>>', self._on_tree_open)
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        # Bottom Controls
        ctrl_frame = Frame(self.sidebar, bg=SIDEBAR_COLOR)
        ctrl_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=20)

        # Selection Count
        Label(ctrl_frame, text="SELECTED", bg=SIDEBAR_COLOR, fg="#888", font=("Helvetica", 10, "bold")).pack(anchor="w")
        self.lbl_count = Label(ctrl_frame, text="0", bg=SIDEBAR_COLOR, fg="white", font=("Helvetica", 32, "bold"))
        self.lbl_count.pack(anchor="w", pady=(0, 15))

        # Buttons (Native macOS buttons don't support bg color well, using simple ones or Frames)
        btn_review = Button(ctrl_frame, text="Review Selection", command=self.open_review, highlightbackground=SIDEBAR_COLOR)
        btn_review.pack(fill=tk.X, pady=5)

        btn_clear = Button(ctrl_frame, text="Clear Cache", command=self.clear_cache, highlightbackground=SIDEBAR_COLOR)
        btn_clear.pack(fill=tk.X, pady=5)


        # --- MAIN AREA CONTENT ---
        # Top Path Bar
        self.top_bar = Frame(self.main_area, bg=BG_COLOR, height=50)
        self.top_bar.pack(fill=tk.X, side=tk.TOP)
        self.top_bar.pack_propagate(False)

        self.path_lbl = Label(self.top_bar, text="Select a folder to start...", bg=BG_COLOR, fg="#888", font=("Helvetica", 14))
        self.path_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Canvas Grid
        self.canvas = Canvas(self.main_area, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = Scrollbar(self.main_area, orient="vertical", command=self.canvas.yview)
        
        self.grid_frame = Frame(self.canvas, bg=BG_COLOR)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.main_area.bind("<Configure>", self._on_resize)

        # --- POPULATE ---
        self.root.after(100, self._populate_roots)
        
        # --- THUMBNAIL WORKER ---
        self.worker_thread = threading.Thread(target=self._thumbnail_worker, daemon=True)
        self.worker_thread.start()

    def _populate_roots(self):
        try:
            # Home
            home = os.path.expanduser("~")
            node_home = self.tree.insert("", "end", text="🏠 Home", values=[home], open=False)
            self.tree.insert(node_home, "end", text="dummy")

            # Volumes
            if os.path.exists("/Volumes"):
                node_vol = self.tree.insert("", "end", text="💾 Volumes", values=["/Volumes"], open=True)
                self._populate_node(node_vol, "/Volumes")
            
            # Common Folders
            for f in ["Desktop", "Downloads", "Documents", "Pictures"]:
                p = os.path.join(home, f)
                if os.path.exists(p):
                    node = self.tree.insert("", "end", text=f"📂 {f}", values=[p], open=False)
                    self.tree.insert(node, "end", text="dummy")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list roots: {e}")

    def _populate_node(self, parent_id, path):
        # Clear dummy
        self.tree.delete(*self.tree.get_children(parent_id))
        
        try:
            items = os.listdir(path)
            # Filter dirs, ignore hidden
            dirs = []
            for name in items:
                if name.startswith('.'): continue
                full = os.path.join(path, name)
                if os.path.isdir(full):
                    dirs.append((name, full))
            
            dirs.sort()
            
            for name, full_path in dirs:
                # Add node
                # Optimization: Check if empty? No, just add dummy.
                oid = self.tree.insert(parent_id, "end", text=f"📁 {name}", values=[full_path])
                self.tree.insert(oid, "end", text="dummy")
                
        except PermissionError:
            self.tree.insert(parent_id, "end", text="⛔ Access Denied")
        except Exception as e:
            print(f"Error reading {path}: {e}")

    def _on_tree_open(self, event):
        item_id = self.tree.focus()
        if not item_id: return
        
        # Check if dummy exists
        children = self.tree.get_children(item_id)
        if len(children) == 1 and self.tree.item(children[0], "text") == "dummy":
            # Expand
            vals = self.tree.item(item_id, "values")
            if vals:
                path = vals[0]
                self._populate_node(item_id, path)

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        if vals:
            path = vals[0]
            if os.path.isdir(path):
                self.load_folder(path)

    # --- GRID LOGIC ---
    def load_folder(self, path):
        if self.current_folder == path: return
        self.current_folder = path
        self.path_lbl.config(text=path)
        
        # Async scan to not freeze UI? For now sync is fast enough for listdir
        try:
            raw = os.listdir(path)
            # Filter images
            exts = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.bmp', '.tiff'}
            self.all_files = [
                os.path.join(path, f) for f in raw 
                if os.path.splitext(f)[1].lower() in exts and not f.startswith('.')
            ]
            self.all_files.sort()
            
            self.render_grid()
        except Exception as e:
            self.path_lbl.config(text=f"Error: {e}")

    def render_grid(self):
        # Clean up
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.thumb_queue = []

        if not self.all_files:
            Label(self.grid_frame, text="No images found", bg=BG_COLOR, fg="#666", font=("Helvetica", 14)).pack(pady=40)
            return

        # Grid Calc
        width = self.root.winfo_width() - 300 # minus sidebar
        if width < 200: width = 800
        cols = max(2, width // 220)
        
        for i, fpath in enumerate(self.all_files):
            r, c = divmod(i, cols)
            
            # Container
            f = Frame(self.grid_frame, bg=CARD_COLOR, width=204, height=204)
            f.grid(row=r, column=c, padx=8, pady=8)
            f.pack_propagate(False)
            
            # Label
            l = Label(f, bg="#222", text="")
            l.place(x=2, y=2, width=200, height=200)
            
            # Selection Highlight
            if fpath in self.selection:
                f.config(bg=SEL_COLOR)
            
            # Bind
            l.bind("<Button-1>", lambda e, p=fpath, widget=f: self.toggle_selection(p, widget))
            f.bind("<Button-1>", lambda e, p=fpath, widget=f: self.toggle_selection(p, widget))
            
            # Queue
            self.thumb_queue.append((fpath, l))

    def toggle_selection(self, path, widget):
        if path in self.selection:
            self.selection.remove(path)
            widget.config(bg=CARD_COLOR)
        else:
            self.selection.append(path)
            widget.config(bg=SEL_COLOR)
        
        self.lbl_count.config(text=str(len(self.selection)))

    # --- THUMBNAIL ENGINE ---
    def _thumbnail_worker(self):
        while self.running:
            if not self.thumb_queue:
                import time
                time.sleep(0.05)
                continue
            
            path, widget = self.thumb_queue.pop(0)
            
            # Check widget existence
            try:
                if not widget.winfo_exists(): continue
            except: continue
            
            thumb = self.get_thumb(path)
            if thumb:
                try:
                    self.root.after(0, lambda w=widget, i=thumb: w.configure(image=i) if w.winfo_exists() else None)
                    # Keep ref? The label keeps ref if configured? No, we need to attach it
                    # But if we attach to widget.image, it works.
                    self.root.after(0, lambda w=widget, i=thumb: setattr(w, 'image', i) if w.winfo_exists() else None)
                except: pass

    def get_thumb(self, path):
        if path in self.photo_cache: return self.photo_cache[path]
        
        c_name = f"{hash(path)}.jpg"
        c_path = os.path.join(CACHE_DIR, c_name)
        
        try:
            if os.path.exists(c_path):
                img = Image.open(c_path)
            else:
                img = Image.open(path)
                img = ImageOps.fit(img, THUMB_SIZE, Image.Resampling.LANCZOS)
                if img.mode != 'RGB': img = img.convert('RGB')
                img.save(c_path, "JPEG", quality=70)
            
            tk_img = ImageTk.PhotoImage(img)
            self.photo_cache[path] = tk_img
            return tk_img
        except: return None

    # --- EVENTS ---
    def _on_resize(self, e):
        # Debounce re-layout?
        # For now just update grid width reference, maybe re-render if col count changes
        self.canvas.itemconfig(self.canvas_window, width=e.width)

    def _on_mousewheel(self, e):
        self.canvas.yview_scroll(int(-1 * e.delta), "units")

    def open_review(self):
        if not self.selection: 
            messagebox.showinfo("Empty", "Select photos first")
            return
        ReviewWindow(self.root, self.selection, self.finish_review)

    def finish_review(self, new_sel):
        self.selection = new_sel
        self.lbl_count.config(text=str(len(self.selection)))
        self.render_grid()

    def clear_cache(self):
        try:
            import shutil
            shutil.rmtree(CACHE_DIR)
            os.makedirs(CACHE_DIR)
            self.photo_cache.clear()
            messagebox.showinfo("Done", "Cache cleared")
        except Exception as e:
            print(e)

# --- REVIEW WINDOW ---
class ReviewWindow:
    def __init__(self, parent, selection, cb):
        self.selection = selection[:]
        self.cb = cb
        self.win = Toplevel(parent)
        self.win.title("Review Selection")
        self.win.geometry("900x700")
        self.win.configure(bg="#111")
        
        # Toolbar
        tb = Frame(self.win, bg="#222")
        tb.pack(fill=tk.X)
        
        Button(tb, text="Up", command=self.mv_up).pack(side=tk.LEFT, padx=5, pady=5)
        Button(tb, text="Down", command=self.mv_down).pack(side=tk.LEFT, padx=5, pady=5)
        Button(tb, text="Remove", command=self.remove, fg="red").pack(side=tk.LEFT, padx=20, pady=5)
        Button(tb, text="Upload to Bunny", command=self.upload, bg="blue", fg="white").pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Panes
        panes = tk.PanedWindow(self.win, orient=tk.HORIZONTAL, bg="black")
        panes.pack(fill=tk.BOTH, expand=True)
        
        self.lb = tk.Listbox(panes, bg="#222", fg="white", font=("Helvetica", 14), selectbackground="blue")
        self.lb.bind("<<ListboxSelect>>", self.on_sel)
        panes.add(self.lb, width=300)
        
        self.prev = Label(panes, bg="black", text="Select item")
        panes.add(self.prev)
        
        self.refresh()

    def refresh(self):
        self.lb.delete(0, tk.END)
        for p in self.selection:
            self.lb.insert(tk.END, os.path.basename(p))

    def on_sel(self, e):
        idx = self.lb.curselection()
        if idx:
            p = self.selection[idx[0]]
            self.show(p)
            
    def show(self, p):
        try:
            img = Image.open(p)
            w, h = self.prev.winfo_width(), self.prev.winfo_height()
            if w < 100: w=600
            if h < 100: h=600
            img.thumbnail((w,h))
            tk = ImageTk.PhotoImage(img)
            self.prev.config(image=tk, text="")
            self.prev.img = tk
        except: pass

    def mv_up(self):
        idx = self.lb.curselection()
        if not idx or idx[0]==0: return
        i = idx[0]
        self.selection[i], self.selection[i-1] = self.selection[i-1], self.selection[i]
        self.refresh()
        self.lb.selection_set(i-1)
        self.on_sel(None)

    def mv_down(self):
        idx = self.lb.curselection()
        if not idx or idx[0]==len(self.selection)-1: return
        i = idx[0]
        self.selection[i], self.selection[i+1] = self.selection[i+1], self.selection[i]
        self.refresh()
        self.lb.selection_set(i+1)
        self.on_sel(None)

    def remove(self):
        idx = self.lb.curselection()
        if idx:
            del self.selection[idx[0]]
            self.refresh()
            self.prev.config(image="", text="Removed")
            self.cb(self.selection)

    def upload(self):
        from tkinter import simpledialog
        name = simpledialog.askstring("Upload", "Folder Name:")
        if not name: return
        
        # Simple upload shim
        threading.Thread(target=self._do_upload, args=(name,)).start()
        
    def _do_upload(self, name):
        import urllib.request
        BUNNY_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
        STORAGE = "kovertripweb"
        
        done = 0
        for i, p in enumerate(self.selection):
            fname = os.path.basename(p)
            ext = os.path.splitext(fname)[1]
            new_n = f"{name}_{i+1}{ext}"
            remote = f"Двухдневка в Альпы/AutoSync/{name}/{new_n}"
            
            safe = "/".join([urllib.parse.quote(x) for x in remote.split('/')])
            url = f"https://storage.bunnycdn.com/{STORAGE}/{safe}"
            
            try:
                with open(p, "rb") as f:
                    req = urllib.request.Request(url, data=f.read(), methods='PUT', headers={"AccessKey": BUNNY_KEY})
                    req.method = "PUT"
                    urllib.request.urlopen(req)
                    done += 1
                    print(f"Uploaded {new_n}")
            except Exception as e: print(e)
            
        self.win.after(0, lambda: messagebox.showinfo("Done", f"Uploaded {done}"))
        self.win.after(0, self.win.destroy)
        self.win.after(0, lambda: self.cb([]))

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoCullApp(root)
    root.mainloop()
