
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Scrollbar, Frame, Label, Button, Toplevel
from PIL import Image, ImageTk

# --- CONFIG ---
THUMB_SIZE = (200, 200)
BG_COLOR = "#1e1e1e"
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
        self.root.geometry("1100x800")
        self.root.configure(bg=BG_COLOR)

        # State
        self.current_folder = ""
        self.all_files = [] # {path, name}
        self.selection = [] # List of full paths (Ordered)
        self.photo_cache = {} # path -> ImageTk
        self.thumb_queue = []
        self.is_loading = False
        
        # UI Layout
        self._setup_sidebar()
        self._setup_main_area()
        
        # Start Thumbnail Worker
        self.running = True
        self.worker_thread = threading.Thread(target=self._thumbnail_worker, daemon=True)
        self.worker_thread.start()

    def _setup_sidebar(self):
        sidebar = Frame(self.root, bg="#111", width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Brand
        Label(sidebar, text="📸 KoverCull", bg="#111", fg="#888", font=("Arial", 16, "bold")).pack(pady=20)

        # Controls
        Button(sidebar, text="📂 Open Folder", command=self.open_folder, 
               bg="#007aff", fg="white", highlightbackground="#111", font=("Arial", 12)).pack(pady=10, padx=20, fill="x")
        
        # Stats
        Label(sidebar, text="CURRENT FOLDER", bg="#111", fg="#666", font=("Arial", 10)).pack(pady=(20,5))
        self.lbl_folder = Label(sidebar, text="None", bg="#111", fg="white", font=("Arial", 11), wraplength=230)
        self.lbl_folder.pack(padx=10)

        Label(sidebar, text="SELECTED", bg="#111", fg="#666", font=("Arial", 10)).pack(pady=(20,5))
        self.lbl_count = Label(sidebar, text="0", bg="#111", fg="white", font=("Arial", 30, "bold"))
        self.lbl_count.pack()

        # Review
        Button(sidebar, text="Review Selection", command=self.open_review, 
               bg="#333", fg="white", highlightbackground="#333").pack(pady=20, padx=20, fill="x")

        # Clear Cache Button
        Button(sidebar, text="Clear Cache", command=self.clear_cache, 
               bg="#333", fg="#ff3b30", highlightbackground="#333").pack(side="bottom", pady=20)

    def _setup_main_area(self):
        self.main_frame = Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(side="right", fill="both", expand=True)

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

    def open_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.load_folder(path)

    def load_folder(self, path):
        self.current_folder = path
        self.lbl_folder.config(text=os.path.basename(path))
        
        # Scan files
        raw = os.listdir(path)
        valid = [f for f in raw if f.lower().endswith(('.jpg','.jpeg','.png','.webp','.heic'))]
        valid.sort()
        
        self.all_files = [os.path.join(path, f) for f in valid]
        self.render_grid()

    def render_grid(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Grid logic
        cols = 4
        # Just create placeholders. Images load async
        
        for i, fpath in enumerate(self.all_files):
            r, c = divmod(i, cols)
            
            # Card Frame
            f = Frame(self.scroll_frame, bg=CARD_COLOR, width=200, height=200)
            f.grid(row=r, column=c, padx=10, pady=10)
            f.pack_propagate(False) # Strict size
            
            # Click handler
            f.bind("<Button-1>", lambda e, p=fpath, widget=f: self.toggle_selection(p, widget))
            
            # Label overlay for selection
            l = Label(f, text="", bg=CARD_COLOR) # border holder
            l.place(x=0, y=0, relwidth=1, relheight=1)
            l.bind("<Button-1>", lambda e, p=fpath, widget=f: self.toggle_selection(p, widget))
            
            # Check if selected
            if fpath in self.selection:
                f.config(bg=SEL_COLOR)
                l.config(bg=SEL_COLOR)

            # Queue thumbnail
            self.thumb_queue.append((fpath, l))

    def _thumbnail_worker(self):
        while self.running:
            if not self.thumb_queue:
                import time
                time.sleep(0.1)
                continue
            
            # LIFO or FIFO? FIFO is better for smooth loading top-down
            # But scrolling jumps... let's just do FIFO
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
                img.thumbnail(THUMB_SIZE)
                # Convert to RGB if needed (png)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(cache_path, "JPEG")
            
            tk_img = ImageTk.PhotoImage(img)
            # Memory cache (small) - maybe limit size?
            # For 8GB RAM, keeping 1000 thumbnails in RAM (200x200) is ~150MB. Safe.
            self.photo_cache[path] = tk_img
            return tk_img
        except Exception:
            return None

    def _set_image(self, widget, img, path):
        try:
            widget.configure(image=img, width=200, height=200)
            widget.image = img # Prevent GC
            
            # Draw persistent selection border/overlay if needed
            if path in self.selection:
                widget.config(bg=SEL_COLOR, borderwidth=4, relief="solid")
        except:
            pass

    def toggle_selection(self, path, frame_widget):
        # find the inner label
        try:
            label = frame_widget.winfo_children()[0]
        except:
            label = frame_widget
            
        if path in self.selection:
            self.selection.remove(path)
            label.config(borderwidth=0, relief="flat")
        else:
            self.selection.append(path)
            label.config(borderwidth=4, relief="solid", bg=SEL_COLOR)
            
        self.lbl_count.config(text=str(len(self.selection)))

    def open_review(self):
        if not self.selection:
            return messagebox.showwarning("Empty", "Select photos first!")
            
        ReviewWindow(self.root, self.selection, self.refresh_selection)

    def refresh_selection(self, new_selection):
        self.selection = new_selection
        self.lbl_count.config(text=str(len(self.selection)))
        # Re-render borders? A bit expensive to map back.
        # User will see when they scroll. 
        # But we should update visible state if possible.
        self.render_grid() # Simplest

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
        self.selection = selection # List of paths
        self.callback = callback
        self.window = Toplevel(parent)
        self.window.title("Review & Sort")
        self.window.geometry("800x600")
        self.window.configure(bg=BG_COLOR)
        
        # Top controls
        top = Frame(self.window, bg=BG_COLOR)
        top.pack(fill="x", padx=10, pady=10)
        
        Label(top, text="Drag items in list to sort (Mock)", bg=BG_COLOR, fg="white").pack(side="left")
        
        Button(top, text="Upload to Bunny", command=self.upload, bg=SEL_COLOR).pack(side="right")
        
        # Split View: List (Order) + Preview
        content = Frame(self.window, bg=BG_COLOR)
        content.pack(fill="both", expand=True)
        
        # Left: Listbox
        self.listbox = tk.Listbox(content, bg="#222", fg="white", selectbackground=SEL_COLOR, selectforeground="black")
        self.listbox.pack(side="left", fill="y", padx=10)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        # Populate
        for p in self.selection:
            self.listbox.insert(tk.END, os.path.basename(p))
            
        # Reorder buttons
        btn_frame = Frame(content, bg=BG_COLOR)
        btn_frame.pack(side="left", fill="y")
        Button(btn_frame, text="⬆️", command=self.move_up).pack(pady=5)
        Button(btn_frame, text="⬇️", command=self.move_down).pack(pady=5)
        Button(btn_frame, text="🗑", command=self.remove_item, fg="red").pack(pady=20)

        # Preview
        self.preview_lbl = Label(content, bg="black")
        self.preview_lbl.pack(side="right", fill="both", expand=True, padx=10)

    def on_select(self, e):
        idx = self.listbox.curselection()
        if idx:
            path = self.selection[idx[0]]
            self.show_preview(path)

    def show_preview(self, path):
        img = Image.open(path)
        # resize to fit
        w = self.preview_lbl.winfo_width()
        h = self.preview_lbl.winfo_height()
        if w < 10 or h < 10: return
        
        img.thumbnail((w, h))
        tk_img = ImageTk.PhotoImage(img)
        self.preview_lbl.config(image=tk_img)
        self.preview_lbl.image = tk_img

    def move_up(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == 0: return
        i = idx[0]
        # Swap logic
        self.selection[i], self.selection[i-1] = self.selection[i-1], self.selection[i]
        self._refresh_list()
        self.listbox.selection_set(i-1)

    def move_down(self):
        idx = self.listbox.curselection()
        if not idx or idx[0] == len(self.selection)-1: return
        i = idx[0]
        self.selection[i], self.selection[i+1] = self.selection[i+1], self.selection[i]
        self._refresh_list()
        self.listbox.selection_set(i+1)

    def remove_item(self):
        idx = self.listbox.curselection()
        if idx:
            del self.selection[idx[0]]
            self._refresh_list()
            self.callback(self.selection)

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for p in self.selection:
            self.listbox.insert(tk.END, os.path.basename(p))

    def upload(self):
        # Call the existing uploader logic or simple python script import
        # For simplicity, just spawn the finder_uploader functions 
        # But we need folder name. 
        from tkinter import simpledialog
        name = simpledialog.askstring("Upload", "Folder Name on Bunny:")
        if not name: return
        
        # UPLOAD
        import urllib.request
        
        BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
        STORAGE_NAME = "kovertripweb"
        
        count = 0
        for i, fpath in enumerate(self.selection):
            fname = os.path.basename(fpath)
            ext = os.path.splitext(fname)[1]
            new_name = f"{name}_{i+1}{ext}"
            remote = f"Двухдневка в Альпы/AutoSync/{name}/{new_name}"
            
            safe_remote = "/".join([urllib.parse.quote(p) for p in remote.split('/')])
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
        
        messagebox.showinfo("Success", f"Uploaded {count} files!")
        self.selection.clear()
        self.callback([])
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoCullApp(root)
    root.mainloop()
