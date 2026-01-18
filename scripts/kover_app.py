
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Frame, Button, Label, Scrollbar, Text

# Check for PIL
try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    tk.messagebox.showerror("Error", "Pillow (PIL) library is missing.\nPlease run: pip install pillow")
    sys.exit(1)

# --- COLORS ---
BG_MAIN = "#1E1E1E"
BG_PANEL = "#252526"
ACCENT = "#0A84FF"
TEXT_MAIN = "#FFFFFF"

class KoverAppDebug:
    def __init__(self, root):
        self.root = root
        self.root.title("Kover Photo Cull (DEBUG V3)")
        self.root.geometry("1100x800")
        self.root.configure(bg=BG_MAIN)
        
        self.current_dir = None
        self.image_files = [] 
        self.selected_files = set()
        self.thumb_queue = []
        self.running = True

        # --- DEBUG CONSOLE (Bottom) ---
        self.console_frame = Frame(self.root, height=150, bg="black")
        self.console_frame.pack(side="bottom", fill="x")
        self.console_frame.pack_propagate(False)
        
        self.console = Text(self.console_frame, bg="black", fg="#00FF00", font=("Consolas", 10))
        self.console.pack(fill="both", expand=True)
        self.log("APP STARTED. Waiting for folder selection...")

        # --- TOOLBAR ---
        self.header = Frame(self.root, bg=BG_PANEL, height=60)
        self.header.pack(fill="x", side="top")
        
        self.btn_open = Button(self.header, text="📂 Open Folder", command=self.select_folder)
        self.btn_open.pack(side="left", padx=20, pady=10)
        
        self.lbl_status = Label(self.header, text="Select a folder", bg=BG_PANEL, fg="white")
        self.lbl_status.pack(side="left")

        # --- MAIN CANVAS ---
        self.canvas = Canvas(self.root, bg=BG_MAIN, highlightthickness=0)
        self.sb = Scrollbar(self.root, command=self.canvas.yview)
        
        self.container = Frame(self.canvas, bg=BG_MAIN)
        self.cv_win = self.canvas.create_window((0,0), window=self.container, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.sb.set)
        
        self.sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._scroll)
        
        # Thread
        threading.Thread(target=self._worker, daemon=True).start()
        
        # Auto-open
        self.root.after(500, self.select_folder)

    def log(self, msg):
        print(msg)
        try:
            self.console.insert("end", f"{msg}\n")
            self.console.see("end")
        except: pass

    def select_folder(self):
        self.log("Opening File Dialog...")
        path = filedialog.askdirectory()
        if not path:
            self.log("No folder selected (Cancelled).")
            return
            
        self.load(path)

    def _scroll(self, e):
        self.canvas.yview_scroll(int(-1*e.delta), "units")

    def load(self, path):
        self.log(f"Selected Path: {path}")
        self.current_dir = path
        self.lbl_status.config(text=path)
        
        # Clear UI
        for w in self.container.winfo_children(): w.destroy()
        self.image_files = []
        self.thumb_queue = []
        
        # Check permissions/formatting
        if not os.path.exists(path):
            self.log("ERROR: Path does not exist!")
            messagebox.showerror("Error", "Path does not exist")
            return
            
        if not os.access(path, os.R_OK):
            self.log("ERROR: No Read Permission!")
            messagebox.showerror("Error", "No Read Permission to this folder. Check System Settings > Privacy > Full Disk Access.")
            return

        # List dir
        try:
            raw_files = os.listdir(path)
            self.log(f"Found {len(raw_files)} items in folder.")
        except Exception as e:
            self.log(f"CRITICAL: Failed to list dir: {e}")
            messagebox.showerror("Error", f"Failed to list: {e}")
            return

        # Filter
        exts = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}
        for f in raw_files:
            if f.startswith('.'): continue
            full = os.path.join(path, f)
            if not os.path.isfile(full): continue
            
            _, ext = os.path.splitext(f)
            if ext.lower() in exts:
                self.image_files.append(full)
        
        self.image_files.sort()
        count = len(self.image_files)
        self.log(f"Filtered {count} valid images.")
        
        if count == 0:
            Label(self.container, text="No images found (jpg, png, heic)", bg=BG_MAIN, fg="white", font=("Arial", 20)).pack(pady=50)
            self.log("Contents of folder (first 10):")
            for x in raw_files[:10]: self.log(f" - {x}")
            return

        # Render Grid
        self.log("Rendering Grid Placeholders...")
        
        w = self.root.winfo_width()
        if w < 200: w = 1000
        cols = max(3, w // 220)
        
        for i, fp in enumerate(self.image_files):
            r, c = divmod(i, cols)
            
            f = Frame(self.container, width=204, height=204, bg="#333")
            f.grid(row=r, column=c, padx=5, pady=5)
            f.pack_propagate(False)
            
            l = Label(f, text=f"Img {i}", bg="#222", fg="white")
            l.place(x=2, y=2, width=200, height=200)
            
            # Simple Selection Logic
            l.bind("<Button-1>", lambda e, p=fp, w=f: self.toggle(p, w))
            
            self.thumb_queue.append((fp, l))
            
        self.log("Grid Rendered. Starting BG Loader...")

    def toggle(self, p, w):
        if p in self.selected_files:
            self.selected_files.remove(p)
            w.config(bg="#333")
        else:
            self.selected_files.add(p)
            w.config(bg="#00FF00")

    def _worker(self):
        while self.running:
            if not self.thumb_queue:
                import time
                time.sleep(0.1)
                continue
                
            path, lbl = self.thumb_queue.pop(0)
            
            try:
                # Debug Check first file
                # self.log(f"Loading thumb: {os.path.basename(path)}")
                
                img = Image.open(path)
                img.thumbnail((200, 200))
                tk_img = ImageTk.PhotoImage(img)
                
                def up(l=lbl, i=tk_img):
                    if l.winfo_exists():
                        l.config(image=i, text="")
                        l.img = i
                
                self.root.after(0, up)
            except Exception as e:
                self.log(f"Failed to load {os.path.basename(path)}: {e}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = KoverAppDebug(root)
        root.mainloop()
    except Exception as e:
        print(f"CRASH: {e}")
