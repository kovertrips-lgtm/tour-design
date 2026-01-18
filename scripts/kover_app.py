
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Canvas, Scrollbar, Frame, Label, Button, Toplevel
from PIL import Image, ImageTk, ImageOps

# --- CONFIG ---
THUMB_SIZE = (200, 200)
BG_COLOR = "#1e1e1e"
SIDEBAR_COLOR = "#252526"
CARD_COLOR = "#2d2d2d"
SEL_COLOR = "#34c759"
TEXT_COLOR = "#ffffff"
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
        self.all_files = [] # {path, name}
        self.selection = [] # List of full paths (Ordered)
        self.photo_cache = {} # path -> ImageTk
        self.thumb_queue = []
        self.running = True
        
        # Styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background=SIDEBAR_COLOR, 
                        foreground="#dddddd", 
                        fieldbackground=SIDEBAR_COLOR,
                        borderwidth=0,
                        font=("Arial", 12))
        style.map('Treeview', background=[('selected', '#37373d')])

        # UI Layout
        # PanedWindow to separate Sidebar and Main
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=BG_COLOR, sashwidth=4)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self._setup_sidebar()
        self._setup_main_area()
        
        self.paned.add(self.sidebar_frame)
        self.paned.add(self.main_frame)
        
        # Initial Population of Tree
        self._populate_drives()
        
        # Start Thumbnail Worker
        self.worker_thread = threading.Thread(target=self._thumbnail_worker, daemon=True)
        self.worker_thread.start()

    def _setup_sidebar(self):
        self.sidebar_frame = Frame(self.paned, bg=SIDEBAR_COLOR, width=300)
        self.sidebar_frame.pack_propagate(False)

        # Header
        Label(self.sidebar_frame, text="📸 KoverCull", bg=SIDEBAR_COLOR, fg="#888", font=("Arial", 16, "bold")).pack(pady=20, padx=10, anchor="w")

        # --- FOLDER TREE ---
        # Scrollbar for tree
        tree_scroll = Scrollbar(self.sidebar_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.sidebar_frame, yscrollcommand=tree_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree_scroll.config(command=self.tree.yview)

        # Bind events
        self.tree.bind('<<TreeviewOpen>>', self._on_tree_open)
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        
        # --- BOTTOM CONTROLS ---
        controls = Frame(self.sidebar_frame, bg=SIDEBAR_COLOR, height=150)
        controls.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=20)
        
        Label(controls, text="SELECTED", bg=SIDEBAR_COLOR, fg="#666", font=("Arial", 10)).pack(anchor="w")
        self.lbl_count = Label(controls, text="0", bg=SIDEBAR_COLOR, fg="white", font=("Arial", 30, "bold"))
        self.lbl_count.pack(anchor="w")
        
        Button(controls, text="Review Selection", command=self.open_review, 
               bg="#333", fg="white", highlightbackground=SIDEBAR_COLOR).pack(fill=tk.X, pady=10)

        Button(controls, text="Clear Cache", command=self.clear_cache, 
               bg=SIDEBAR_COLOR, fg="#ff3b30", borderwidth=0, highlightbackground=SIDEBAR_COLOR).pack(anchor="w")

    def _setup_main_area(self):
        self.main_frame = Frame(self.paned, bg=BG_COLOR)

        # Top Bar (Path)
        self.path_bar = Label(self.main_frame, text="Select a folder...", bg=BG_COLOR, fg="#888", font=("Arial", 12), anchor="w", padx=20)
        self.path_bar.pack(fill=tk.X, pady=10)

        # Scrollable Canvas
        self.canvas = Canvas(self.main_frame, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        
        self.scroll_frame = Frame(self.canvas, bg=BG_COLOR)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.main_frame.bind("<Configure>", self._on_resize)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta)), "units")

    def _on_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # --- TREE VIEW LOGIC ---
    def _populate_drives(self):
        # Add Root Locations
        # Home
        home_path = os.path.expanduser("~")
        node_home = self.tree.insert("", "end", text="🏠 Home", values=[home_path], open=False)
        self.tree.insert(node_home, "end", text="dummy") # dummy to allow expansion

        # Volumes
        node_vol = self.tree.insert("", "end", text="💾 Volumes", values=["/Volumes"], open=True)
        self._populate_node(node_vol, "/Volumes")

        # Desktop
        desktop = os.path.join(home_path, "Desktop")
        node_desk = self.tree.insert("", "end", text="🖥 Desktop", values=[desktop], open=False)
        self.tree.insert(node_desk, "end", text="dummy")

        # Documents
        docs = os.path.join(home_path, "Documents")
        node_docs = self.tree.insert("", "end", text="📄 Documents", values=[docs], open=False)
        self.tree.insert(node_docs, "end", text="dummy")
        
    def _populate_node(self, parent_id, path):
        # Remove dummy
        self.tree.delete(*self.tree.get_children(parent_id))
        
        try:
            items = os.listdir(path)
            # Filter for Directories only for the tree
            dirs = [d for d in items if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
            dirs.sort()
            
            for d in dirs:
                full_path = os.path.join(path, d)
                # Check if empty or has children (optimization: always add dummy for dirs)
                oid = self.tree.insert(parent_id, "end", text=d, values=[full_path])
                self.tree.insert(oid, "end", text="dummy")
        except PermissionError:
            pass
        except OSError:
            pass

    def _on_tree_open(self, event):
        item_id = self.tree.focus()
        if not item_id: return
        
        # Logic: if child is dummy, populate.
        children = self.tree.get_children(item_id)
        if len(children) == 1 and self.tree.item(children[0], "text") == "dummy":
            path = self.tree.item(item_id, "values")[0]
            self._populate_node(item_id, path)

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        path = self.tree.item(selected[0], "values")[0]
        if path and os.path.isdir(path):
            self.load_folder(path)

    # --- MAIN LOGIC ---
    def load_folder(self, path):
        if self.current_folder == path: return
        self.current_folder = path
        self.path_bar.config(text=path)
        
        # Scan files
        try:
            raw = os.listdir(path)
            valid = [f for f in raw if f.lower().endswith(('.jpg','.jpeg','.png','.webp','.heic')) and not f.startswith('.')]
            valid.sort()
            
            self.all_files = [os.path.join(path, f) for f in valid]
            self.render_grid()
        except Exception as e:
            self.path_bar.config(text=f"Error accessing: {path}")

    def render_grid(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Clear queue
        self.thumb_queue = []

        if not self.all_files:
            Label(self.scroll_frame, text="No photos found.", bg=BG_COLOR, fg="#666", font=("Arial", 14)).pack(pady=50)
            return

        # Adaptive Grid Config
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100: canvas_width = 800 # default
        
        # We assume card width ~220px (200 + padding)
        cols = max(3, canvas_width // 230)
        
        for i, fpath in enumerate(self.all_files):
            r, c = divmod(i, cols)
            
            # Card Container
            f = Frame(self.scroll_frame, bg=CARD_COLOR, width=204, height=204)
            f.grid(row=r, column=c, padx=8, pady=8)
            f.pack_propagate(False) # Strict size
            
            # Inner Label (Image Holder)
            l = Label(f, text="", bg="#222") 
            l.place(x=2, y=2, width=200, height=200)
            
            # Bindings
            l.bind("<Button-1>", lambda e, p=fpath, widget=f: self.toggle_selection(p, widget))
            f.bind("<Button-1>", lambda e, p=fpath, widget=f: self.toggle_selection(p, widget))
            
            # Check if selected
            if fpath in self.selection:
                f.config(bg=SEL_COLOR)
                l.config(bg=SEL_COLOR, borderwidth=0) # Border effect via frame bg

            # Queue thumbnail
            self.thumb_queue.append((fpath, l))

    def _thumbnail_worker(self):
        while self.running:
            if not self.thumb_queue:
                import time
                time.sleep(0.1)
                continue
            
            fpath, label_widget = self.thumb_queue.pop(0)
            
            # Check if widget still exists
            try:
                if not label_widget.winfo_exists():
                    continue
            except:
                continue

            # Load/Generate Thumb
            thumb = self.get_thumbnail(fpath)
            
            # Update UI on main thread
            if thumb:
                self.root.after(0, lambda w=label_widget, i=thumb, p=fpath: self._set_image(w, i, p))

    def get_thumbnail(self, path):
        # Check memory cache
        if path in self.photo_cache:
            return self.photo_cache[path]
        
        # Check disk cache
        hash_name = str(hash(path)) + ".jpg"
        cache_path = os.path.join(CACHE_DIR, hash_name)
        
        try:
            if os.path.exists(cache_path):
                img = Image.open(cache_path)
            else:
                # Generate
                img = Image.open(path)
                img.thumbnail(THUMB_SIZE) # Preserves aspect ratio
                # Square crop (simple center)
                # For grid consistency, maybe allow varying aspect or force square?
                # Let's force square for neater grid
                img = ImageOps.fit(img, THUMB_SIZE, Image.LANCZOS)
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(cache_path, "JPEG", quality=70)
            
            tk_img = ImageTk.PhotoImage(img)
            # Memory cache limit
            if len(self.photo_cache) > 500:
                # Remove random or old? Simple clear for now or simple FIFO limit isn't implemented.
                # Just lazy limit: don't cache if full
                pass
            else:
                self.photo_cache[path] = tk_img
            return tk_img
        except Exception:
            return None

    def _set_image(self, widget, img, path):
        try:
            widget.configure(image=img)
            widget.image = img # Prevent GC
        except:
            pass

    def toggle_selection(self, path, frame_widget):
        if path in self.selection:
            self.selection.remove(path)
            frame_widget.config(bg=CARD_COLOR)
        else:
            self.selection.append(path)
            frame_widget.config(bg=SEL_COLOR)
            
        self.lbl_count.config(text=str(len(self.selection)))

    def open_review(self):
        if not self.selection:
            return messagebox.showwarning("Empty", "Select photos first!")
            
        ReviewWindow(self.root, self.selection, self.refresh_selection)

    def refresh_selection(self, new_selection):
        self.selection = new_selection
        self.lbl_count.config(text=str(len(self.selection)))
        self.render_grid()

    def clear_cache(self):
        import shutil
        try:
            shutil.rmtree(CACHE_DIR)
            os.makedirs(CACHE_DIR)
            self.photo_cache.clear()
            messagebox.showinfo("Done", "Cache cleared")
        except:
            pass

class ReviewWindow:
    def __init__(self, parent, selection, callback):
        self.selection = selection[:] # Copy
        self.callback = callback
        self.window = Toplevel(parent)
        self.window.title("Review & Sort")
        self.window.geometry("900x700")
        self.window.configure(bg=BG_COLOR)
        
        # --- UI FOR REVIEW ---
        # Top toolbar
        toolbar = Frame(self.window, bg="#111")
        toolbar.pack(fill=tk.X, padx=0)
        
        Button(toolbar, text="⬆ Move Up", command=self.move_up, bg="#444", fg="white").pack(side=tk.LEFT, padx=5, pady=10)
        Button(toolbar, text="⬇ Move Down", command=self.move_down, bg="#444", fg="white").pack(side=tk.LEFT, padx=5, pady=10)
        Button(toolbar, text="🗑 Remove", command=self.remove_item, bg="#b3261e", fg="white").pack(side=tk.LEFT, padx=20, pady=10)
        
        Button(toolbar, text="🚀 Upload to Bunny", command=self.upload, bg=SEL_COLOR, fg="white", font=("Arial", 14, "bold")).pack(side=tk.RIGHT, padx=10, pady=10)

        # Split: List vs Preview
        main_review = tk.PanedWindow(self.window, orient=tk.HORIZONTAL, bg=BG_COLOR)
        main_review.pack(fill=tk.BOTH, expand=True)
        
        # Left: Listbox
        self.listbox = tk.Listbox(main_review, bg="#222", fg="white", selectbackground=SEL_COLOR, selectforeground="black", font=("Arial", 14))
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        main_review.add(self.listbox, minsize=250)
        
        # Right: Image Preview
        self.preview_lbl = Label(main_review, bg="black", text="Select an image")
        main_review.add(self.preview_lbl, minsize=400)
        
        self._refresh_list()

    def on_select(self, e):
        idx = self.listbox.curselection()
        if idx:
            path = self.selection[idx[0]]
            self.show_preview(path)

    def show_preview(self, path):
        # Full res preview or large wait?
        # Let's try loading full res but scale it to window
        try:
            img = Image.open(path)
            
            # Scale
            w_avail = self.preview_lbl.winfo_width()
            h_avail = self.preview_lbl.winfo_height()
            if w_avail < 100: w_avail = 600
            if h_avail < 100: h_avail = 600
            
            img.thumbnail((w_avail, h_avail))
            tk_img = ImageTk.PhotoImage(img)
            self.preview_lbl.config(image=tk_img, text="")
            self.preview_lbl.image = tk_img
        except:
            pass

    def move_up(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == 0: return
        i = idx[0]
        self.selection[i], self.selection[i-1] = self.selection[i-1], self.selection[i]
        self._refresh_list()
        self.listbox.selection_set(i-1)
        self.listbox.see(i-1)

    def move_down(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == len(self.selection)-1: return
        i = idx[0]
        self.selection[i], self.selection[i+1] = self.selection[i+1], self.selection[i]
        self._refresh_list()
        self.listbox.selection_set(i+1)
        self.listbox.see(i+1)

    def remove_item(self):
        idx = self.listbox.curselection()
        if idx:
            del self.selection[idx[0]]
            self._refresh_list()
            self.preview_lbl.config(image="", text="Removed")
            self.callback(self.selection)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for p in self.selection:
            self.listbox.insert(tk.END, f"{os.path.basename(p)}")

    def upload(self):
        from tkinter import simpledialog
        name = simpledialog.askstring("Upload", "Enter Folder Name on Bunny (e.g. 'Paris_Trip'):")
        if not name: return
        
        # UPLOAD
        import urllib.request
        
        BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
        STORAGE_NAME = "kovertripweb"
        
        # Progress Dialog
        progress_win = Toplevel(self.window)
        progress_win.title("Uploading...")
        progress_win.geometry("400x150")
        lbl = Label(progress_win, text="Starting upload...", font=("Arial", 12), pady=20)
        lbl.pack()
        
        # Separate thread for upload
        def run_upload():
            count = 0
            errs = 0
            total = len(self.selection)
            
            for i, fpath in enumerate(self.selection):
                fname = os.path.basename(fpath)
                ext = os.path.splitext(fname)[1]
                
                # Sanitize new name
                new_name = f"{name}_{i+1}{ext}"
                new_name = new_name.replace(" ", "_")
                
                # Bunny Path
                remote_dir = f"Двухдневка в Альпы/AutoSync/{name}"
                remote_path = f"{remote_dir}/{new_name}"
                
                # Update UI
                lbl.config(text=f"Uploading {i+1}/{total}:\n{new_name}")
                
                # Bunny logic
                safe_remote = "/".join([urllib.parse.quote(p) for p in remote_path.split('/')])
                url = f"https://storage.bunnycdn.com/{STORAGE_NAME}/{safe_remote}"
                
                headers = {"AccessKey": BUNNY_API_KEY, "Content-Type": "application/octet-stream"}
                try:
                    with open(fpath, "rb") as f:
                        req = urllib.request.Request(url, data=f.read(), headers=headers, method='PUT')
                        urllib.request.urlopen(req)
                        count += 1
                        print(f"Uploaded {new_name}")
                except Exception as e:
                    print(e)
                    errs += 1
            
            self.window.after(0, lambda: messagebox.showinfo("Done", f"Uploaded: {count}\nErrors: {errs}"))
            self.window.after(0, progress_win.destroy)
            self.window.after(0, self.window.destroy) # Close review
            self.window.after(0, lambda: self.callback([])) # Clear main selection

        threading.Thread(target=run_upload).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoCullApp(root)
    root.mainloop()
