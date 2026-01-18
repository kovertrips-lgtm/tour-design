
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Frame, Button, Label, Scrollbar

# Check for PIL
try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    tk.messagebox.showerror("Error", "Pillow (PIL) library is missing.\nPlease run: pip install pillow")
    sys.exit(1)

# --- COLORS & STYLES ---
BG_MAIN = "#1E1E1E"       # Dark Slate
BG_PANEL = "#252526"      # Slightly lighter
ACCENT = "#0A84FF"        # iOS Blue
SUCCESS = "#30D158"       # iOS Green
TEXT_MAIN = "#FFFFFF"
TEXT_SUB = "#AAAAAA"

class KoverAppV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Kover Photo Cull V2")
        self.root.geometry("1100x800")
        self.root.configure(bg=BG_MAIN)
        
        # State
        self.current_dir = None
        self.image_files = [] # list of full paths
        self.selected_files = set() # set of full paths
        self.thumbnails = {} # path -> PhotoImage
        self.thumb_queue = [] # list of (path, label_widget)
        self.running = True

        # --- UI LAYOUT ---
        # 1. Header Toolbar
        self.header = Frame(self.root, bg=BG_PANEL, height=60)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.btn_open = Button(self.header, text="📂 Open Folder", command=self.select_folder, 
                               font=("System", 14), highlightbackground=BG_PANEL)
        self.btn_open.pack(side="left", padx=20, pady=10)

        self.lbl_status = Label(self.header, text="No folder selected", bg=BG_PANEL, fg=TEXT_SUB, font=("System", 12))
        self.lbl_status.pack(side="left", padx=10)

        self.btn_review = Button(self.header, text="Review & Upload (0)", state="disabled", command=self.open_review_window,
                                 font=("System", 14, "bold"), highlightbackground=BG_PANEL, fg=ACCENT)
        self.btn_review.pack(side="right", padx=20)

        # 2. Main Canvas (Gallery)
        self.canvas_frame = Frame(self.root, bg=BG_MAIN)
        self.canvas_frame.pack(fill="both", expand=True)

        self.v_scroll = Scrollbar(self.canvas_frame, orient="vertical")
        self.canvas = Canvas(self.canvas_frame, bg=BG_MAIN, highlightthickness=0, yscrollcommand=self.v_scroll.set)
        self.v_scroll.config(command=self.canvas.yview)
        
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grid_container = Frame(self.canvas, bg=BG_MAIN)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_container, anchor="nw")

        # Events
        self.grid_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind("<Configure>", self._on_resize)
        
        # 3. Start Background Threads
        self.thread = threading.Thread(target=self._thumb_loader, daemon=True)
        self.thread.start()

        # Initial Prompt
        self.select_folder()

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * event.delta), "units")
        
    def _on_resize(self, event):
        # Resize canvas window to match canvas width (for flow layout if we used pack, but we use grid)
        # Just ensure container is at least canvas width
        w = event.width - 20 # scrollbar buffer
        self.canvas.itemconfig(self.canvas_window, width=w)

    # --- LOGIC ---

    def select_folder(self):
        # Using Native OS Dialog - This is the key fix for "can't select"
        path = filedialog.askdirectory()
        if path:
            self.load_images(path)

    def load_images(self, path):
        self.current_dir = path
        self.lbl_status.config(text=f"📂 {os.path.basename(path)}")
        
        # Clear UI
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        
        self.image_files = []
        self.thumbnails = {}
        self.thumb_queue = []
        self.selected_files = set()
        self.update_review_btn()

        # Scan
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
        try:
            files = sorted([os.path.join(path, f) for f in os.listdir(path) 
                            if os.path.splitext(f.lower())[1] in valid_exts and not f.startswith(".")])
            self.image_files = files
            
            if not files:
                Label(self.grid_container, text="No images found.", bg=BG_MAIN, fg=TEXT_SUB, font=("System", 18)).pack(pady=50)
                return
            
            self._render_grid()
            
        except OSError as e:
            messagebox.showerror("Error", f"Access Denied: {e}")

    def _render_grid(self):
        # Simple Flow Layout using Grid
        # Calculate columns
        win_width = self.root.winfo_width()
        if win_width < 200: win_width = 1000
        
        col_count = max(3, win_width // 220)
        
        for i, fpath in enumerate(self.image_files):
            r, c = divmod(i, col_count)
            
            # Card Frame
            card = Frame(self.grid_container, bg="#333", width=200, height=200)
            card.grid(row=r, column=c, padx=5, pady=5)
            card.pack_propagate(False)
            
            # Image Label
            lbl = Label(card, bg="#222", text="Loading...")
            lbl.place(relx=0.5, rely=0.5, anchor="center", width=190, height=190)
            
            # Bind Click
            # Use closure defaults to capture current fpath/card
            lbl.bind("<Button-1>", lambda e, p=fpath, w=card: self.toggle_select(p, w))
            card.bind("<Button-1>", lambda e, p=fpath, w=card: self.toggle_select(p, w))
            
            self.thumb_queue.append((fpath, lbl))

    def _thumb_loader(self):
        while self.running:
            if not self.thumb_queue:
                import time
                time.sleep(0.05)
                continue
            
            # Process one
            fpath, lbl = self.thumb_queue.pop(0) # FIFO
            
            # Skip if widget died
            try:
                if not lbl.winfo_exists(): continue
            except: continue
            
            # Generate or Cache
            thumb = self._get_thumbnail(fpath)
            
            # Update Main Thread
            if thumb:
                def update(l=lbl, t=thumb):
                    if l.winfo_exists():
                        l.config(text="", image=t)
                        l.image = t # keep ref
                try:
                    self.root.after(0, update)
                except: pass

    def _get_thumbnail(self, path):
        # In-memory cache first
        if path in self.thumbnails:
            return self.thumbnails[path]
            
        try:
            # Load and Resize
            img = Image.open(path)
            img.thumbnail((190, 190))
            
            # Center Crop to Square (simulate object-fit: cover)
            w, h = img.size
            size = 190
            
            # Only crop if it's larger
            # Simple approach: just use the thumbnail as is, black bars if aspect differs
            # For "Application" like feel, let's just make it a PhotoImage
            
            tk_img = ImageTk.PhotoImage(img)
            # self.thumbnails[path] = tk_img # Cache in memory? Might eat RAM. 
            # Use LRU logic? For now, we rely on OS file cache for speed on re-read,
            # or we can cache tiny thumbnails.
            
            return tk_img
        except Exception as e:
            print(f"Thumb error: {e}")
            return None

    def toggle_select(self, path, card_widget):
        if path in self.selected_files:
            self.selected_files.remove(path)
            card_widget.configure(bg="#333") # Default border
        else:
            self.selected_files.add(path)
            card_widget.configure(bg=SUCCESS) # Green border
            
        self.update_review_btn()

    def update_review_btn(self):
        count = len(self.selected_files)
        self.btn_review.config(text=f"Review & Upload ({count})", 
                               state="normal" if count > 0 else "disabled")

    # --- REVIEW WINDOW ---
    def open_review_window(self):
        ReviewWindow(self.root, list(self.selected_files), self.on_upload_finished)

    def on_upload_finished(self, uploaded_files):
        # Clear selection of uploaded files
        for p in uploaded_files:
            if p in self.selected_files:
                self.selected_files.remove(p)
        
        # Redraw grid borders
        # (A bit inefficient to scan all, but safe)
        # Actually easier to just reload current folder to refresh state
        self.load_images(self.current_dir)


class ReviewWindow:
    def __init__(self, parent, files, callback):
        self.files = sorted(files)
        self.callback = callback
        self.win = tk.Toplevel(parent)
        self.win.title(f"Review {len(files)} Photos")
        self.win.geometry("800x600")
        self.win.configure(bg=BG_MAIN)

        # Toolbar
        self.tb = Frame(self.win, bg=BG_PANEL, height=50)
        self.tb.pack(fill="x", side="top")
        
        Button(self.tb, text="Cancel", command=self.win.destroy).pack(side="left", padx=10, pady=10)
        
        self.btn_up = Button(self.tb, text="🚀 Upload to Bunny", command=self.start_upload, 
                             bg=ACCENT, fg="black", font=("System", 12, "bold"))
        self.btn_up.pack(side="right", padx=10, pady=10)

        # List
        self.listbox = tk.Listbox(self.win, bg="#333", fg="white", font=("System", 14), selectbackground=ACCENT)
        self.listbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        for f in self.files:
            self.listbox.insert("end", os.path.basename(f))

    def start_upload(self):
        from tkinter import simpledialog
        folder_name = simpledialog.askstring("Upload", "Enter Trip/Event Name (e.g. Alps_2024):", parent=self.win)
        
        if not folder_name: return
        
        # Disable button
        self.btn_up.config(state="disabled", text="Uploading...")
        
        # Thread it
        threading.Thread(target=self._upload_thread, args=(folder_name,)).start()

    def _upload_thread(self, folder_name):
        import urllib.request, urllib.parse
        
        BUNNY_API = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
        STORAGE_NAME = "kovertripweb"
        
        success_list = []
        errors = 0
        
        total = len(self.files)
        
        for i, local_path in enumerate(self.files):
            try:
                fname = os.path.basename(local_path)
                ext = os.path.splitext(fname)[1]
                
                # Sanitize
                clean_folder = "".join(c for c in folder_name if c.isalnum() or c in (' ', '_', '-')).strip()
                clean_folder = clean_folder.replace(" ", "_")
                
                new_name = f"{clean_folder}_{i+1}{ext}"
                
                # Path: Двухдневка в Альпы/AutoSync/{Name}/{file}
                # Using Quote for URL safety
                remote_path_raw = f"Двухдневка в Альпы/AutoSync/{clean_folder}/{new_name}"
                remote_path_enc = "/".join([urllib.parse.quote(seg) for seg in remote_path_raw.split('/')])
                
                url = f"https://storage.bunnycdn.com/{STORAGE_NAME}/{remote_path_enc}"
                
                # Read Data & Upload
                with open(local_path, "rb") as f:
                    data = f.read()
                
                req = urllib.request.Request(url, data=data, method="PUT")
                req.add_header("AccessKey", BUNNY_API)
                req.add_header("Content-Type", "application/octet-stream")
                
                urllib.request.urlopen(req)
                success_list.append(local_path)
                print(f"Uploaded: {new_name}")
                
            except Exception as e:
                print(f"Failed {local_path}: {e}")
                errors += 1
        
        # Finish
        self.win.after(0, lambda: self._finish(success_list, errors))

    def _finish(self, success_list, errors):
        messagebox.showinfo("Upload Complete", f"Successfully uploaded: {len(success_list)}\nErrors: {errors}")
        self.callback(success_list)
        self.win.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = KoverAppV2(root)
    root.mainloop()
