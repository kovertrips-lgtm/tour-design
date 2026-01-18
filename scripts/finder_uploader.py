import os
import sys
import json
import urllib.parse
import urllib.request
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox

# --- CONFIG ---
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_NAME = "kovertripweb"

# --- APPLESCRIPT TO GET FINDER SELECTION ---
def get_finder_selection():
    script = '''
    tell application "Finder"
        set selectedItems to selection
        set pathList to {}
        repeat with itemRef in selectedItems
            set end of pathList to POSIX path of (itemRef as text)
        end repeat
        set AppleScript's text item delimiters to "\\n"
        return pathList as text
    end tell
    '''
    try:
        # Run AppleScript
        result = subprocess.check_output(['osascript', '-e', script], text=True)
        # Split by newline and filter empty
        paths = [p.strip() for p in result.split('\n') if p.strip()]
        return paths
    except Exception as e:
        print(f"Error getting selection: {e}")
        return []

def upload_bunny(local_path, target_folder, index):
    filename = os.path.basename(local_path)
    ext = os.path.splitext(filename)[1]
    
    # New Name: target_folder_1.jpg
    new_name = f"{target_folder}_{index}{ext}"
    
    # Remote Path
    remote_path = f"Двухдневка в Альпы/AutoSync/{target_folder}/{new_name}"
    
    # URL Encode
    safe_remote = "/".join([urllib.parse.quote(p) for p in remote_path.split('/')])
    url = f"https://storage.bunnycdn.com/{STORAGE_NAME}/{safe_remote}"
    
    headers = {
        "AccessKey": BUNNY_API_KEY, 
        "Content-Type": "application/octet-stream"
    }
    
    try:
        with open(local_path, "rb") as f:
            req = urllib.request.Request(url, data=f.read(), headers=headers, method='PUT')
            with urllib.request.urlopen(req) as res:
                return res.status == 201
    except Exception as e:
        print(f"❌ Upload error {filename}: {e}")
        return False

def main():
    # 1. Hide the main Tkinter window (we only need dialogs)
    root = tk.Tk()
    root.withdraw()
    
    # 2. Get Selection
    print("👀 Asking Finder for selection...")
    files = get_finder_selection()
    
    valid_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic'))]
    
    if not valid_files:
        messagebox.showwarning("Kover Uploader", "⚠️ Ничего не выбрано!\n\n1. Откройте Finder.\n2. Выделите фотографии.\n3. Запустите программу снова.")
        sys.exit()
    
    # 3. Ask for Folder Name
    folder_name = simpledialog.askstring("Kover Uploader", f"Выбрано фото: {len(valid_files)}\n\nКуда загружаем? (Название папки на Bunny):", initialvalue="hallstatt_best")
    
    if not folder_name:
        sys.exit() # Cancelled
        
    folder_name = folder_name.strip()
    
    # 4. Upload Loop
    success_count = 0
    errors = []
    
    # Simple Progress Window (Optional refinement: Real progress bar. For now, just blocking)
    # Let's verify file access first
    files_access_ok = all(os.access(f, os.R_OK) for f in valid_files)
    if not files_access_ok:
         messagebox.showerror("Error", "Нет доступа к файлам. Возможно, это сетевой диск и он отвалился.")
         sys.exit()

    print(f"🚀 Uploading {len(valid_files)} items to '{folder_name}'...")
    
    # We can use a simple Toplevel for progress if we want, but let's keep it simple:
    # Just do it. Cursor might spin.
    
    for i, fpath in enumerate(valid_files):
        if upload_bunny(fpath, folder_name, i+1):
            success_count += 1
        else:
            errors.append(os.path.basename(fpath))
            
    # 5. Result
    msg = f"✅ Готово!\nЗагружено: {success_count} из {len(valid_files)}"
    if errors:
        msg += f"\n\n❌ Ошибки ({len(errors)}):\n" + "\n".join(errors)
        messagebox.showwarning("Результат", msg)
    else:
        messagebox.showinfo("Результат", msg)

if __name__ == "__main__":
    main()
