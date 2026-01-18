
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

def get_finder_selection():
    # AppleScript to get selection from the *last active* Finder window
    # We iterate windows to find one with selection
    script = '''
    tell application "Finder"
        set windowList to every window
        repeat with w in windowList
            try
                set sel to selection of w
                if (count of sel) > 0 then
                    set pathList to {}
                    repeat with itemRef in sel
                        set end of pathList to POSIX path of (itemRef as text)
                    end repeat
                    set AppleScript's text item delimiters to "\\n"
                    return pathList as text
                end if
            end try
        end repeat
        return ""
    end tell
    '''
    try:
        result = subprocess.check_output(['osascript', '-e', script], text=True)
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
    root = tk.Tk()
    root.withdraw()
    
    # Check CLI args first (Drag & Drop)
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Fallback to finding selection in Finder
        files = get_finder_selection()
    
    valid_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic', '.mov', '.mp4'))]
    
    if not valid_files:
        messagebox.showwarning("Kover Uploader", "⚠️ Ничего не выбрано!\n\nПеретащите фото на иконку программы\nИЛИ\nВыделите их в Finder и запустите программу.")
        sys.exit()
    
    # Ask for Folder Name
    folder_name = simpledialog.askstring("Kover Uploader", f"Выбрано файлов: {len(valid_files)}\n\nКуда загружаем? (Название папки):", initialvalue="hallstatt_best")
    
    if not folder_name:
        sys.exit() # Cancelled
        
    folder_name = folder_name.strip()
    
    # Upload
    success_count = 0
    errors = []
    
    # Blocking loop (simple)
    for i, fpath in enumerate(valid_files):
        if upload_bunny(fpath, folder_name, i+1):
            success_count += 1
        else:
            errors.append(os.path.basename(fpath))
            
    # Result
    msg = f"✅ Готово!\nЗагружено: {success_count} из {len(valid_files)}"
    if errors:
        msg += f"\n\n❌ Ошибки ({len(errors)}):\n" + "\n".join(errors)
        messagebox.showwarning("Результат", msg)
        print(msg)
    else:
        messagebox.showinfo("Результат", msg)
        print(msg)

if __name__ == "__main__":
    main()
