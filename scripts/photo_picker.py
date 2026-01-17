
import os
import sys
import json
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes

# --- CONFIG ---
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_NAME = "kovertripweb"
PORT = 8000
TARGET_FOLDER = "" # Will be set from args

# HTML TEMPLATE
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kover Photo Picker</title>
    <style>
        body { background: #111; color: white; font-family: system-ui, sans-serif; padding: 20px; margin: 0; }
        .header { position: sticky; top: 0; background: #111; z-index: 100; padding: 10px 0; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center;}
        h1 { margin: 0; font-size: 20px; }
        
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); 
            gap: 15px; 
            padding: 20px 0; 
        }
        
        .card { 
            position: relative; 
            aspect-ratio: 3/4; 
            background: #222; 
            border-radius: 12px; 
            overflow: hidden; 
            cursor: pointer; 
            border: 3px solid transparent; 
            transition: 0.1s;
        }
        
        .card:hover { transform: scale(1.02); }
        
        .card.selected { 
            border-color: #BDFF00; 
            box-shadow: 0 0 15px rgba(189, 255, 0, 0.3);
        }
        
        .card img { width: 100%; height: 100%; object-fit: cover; }
        
        .card .check {
            position: absolute; top: 10px; right: 10px;
            width: 24px; height: 24px;
            background: #BDFF00; color: black;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: bold;
            opacity: 0;
            transform: scale(0);
            transition: 0.2s;
        }
        
        .card.selected .check { opacity: 1; transform: scale(1); }
        
        .card .name {
            position: absolute; bottom: 0; left: 0; right: 0;
            background: rgba(0,0,0,0.7);
            padding: 5px; font-size: 10px; text-align: center; color: #aaa;
        }
        
        #upload-btn {
            background: #29B6F6; color: white; border: none; 
            padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer;
            font-size: 16px;
        }
        #upload-btn:disabled { background: #444; cursor: not-allowed; }
        
        .target-input {
            background: #333; color: white; border: 1px solid #555; padding: 8px; border-radius: 6px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📸 Выбери фото для сайта</h1>
            <div style="font-size: 12px; color: #888;">Папка: <span id="path-display">...</span></div>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            <input type="text" id="bunny-folder" class="target-input" value="hallstatt_best" placeholder="Папка на Bunny">
            <button id="upload-btn" onclick="uploadSelected()">Загрузить (0)</button>
        </div>
    </div>
    
    <div class="grid" id="grid"></div>

    <script>
        let selectedFiles = new Set();
        let allFiles = [];

        async function loadImages() {
            const res = await fetch('/api/list');
            const data = await res.json();
            allFiles = data.files;
            document.getElementById('path-display').innerText = data.path;
            
            const grid = document.getElementById('grid');
            
            if (allFiles.length === 0) {
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 50px;">Фото не найдены (.jpg, .png) <br> Или Google Drive тупит (долго грузит).</div>';
                return;
            }

            allFiles.forEach(f => {
                const div = document.createElement('div');
                div.className = 'card';
                div.onclick = () => toggleSelect(div, f);
                div.innerHTML = `
                    <img src="/image/${encodeURIComponent(f)}" loading="lazy">
                    <div class="check">✓</div>
                    <div class="name">${f}</div>
                `;
                grid.appendChild(div);
            });
        }

        function toggleSelect(el, filename) {
            if (selectedFiles.has(filename)) {
                selectedFiles.delete(filename);
                el.classList.remove('selected');
            } else {
                selectedFiles.add(filename);
                el.classList.add('selected');
            }
            updateBtn();
        }

        function updateBtn() {
            const btn = document.getElementById('upload-btn');
            btn.innerText = `Загрузить (${selectedFiles.size})`;
            btn.disabled = selectedFiles.size === 0;
            btn.style.background = selectedFiles.size > 0 ? '#29B6F6' : '#444';
        }

        async function uploadSelected() {
            const btn = document.getElementById('upload-btn');
            const folderName = document.getElementById('bunny-folder').value;
            if(!folderName) return alert("Введи имя папки для Bunny!");
            
            btn.disabled = true;
            btn.innerText = "Загрузка... 👀";
            
            const payload = {
                files: Array.from(selectedFiles),
                target: folderName
            };

            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                alert(`Готово! Загружено: ${result.success}. \nТеперь скажи Агенту обновить сайт.`);
                selectedFiles.clear();
                document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
                updateBtn();
            } catch (e) {
                alert("Ошибка: " + e);
                btn.disabled = false;
            }
        }

        loadImages();
    </script>
</body>
</html>
"""

def upload_to_bunny(local_path, remote_path):
    url = f"https://storage.bunnycdn.com/{STORAGE_NAME}/{urllib.parse.quote(remote_path)}"
    headers = { "AccessKey": BUNNY_API_KEY, "Content-Type": "application/octet-stream" }
    
    try:
        with open(local_path, "rb") as f:
            req = urllib.request.Request(url, data=f.read(), headers=headers, method='PUT')
            with urllib.request.urlopen(req) as response:
                return response.status == 201
    except Exception as e:
        print(f"Upload error: {e}")
        return False

class PhotoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve main page
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
            return

        # API: List files
        if self.path == '/api/list':
            files = []
            try:
                # LIST DIR (Only Images)
                for f in os.listdir(TARGET_FOLDER):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        # Check size > 10KB to avoid ghost files
                        fp = os.path.join(TARGET_FOLDER, f)
                        if os.path.getsize(fp) > 10000:
                            files.append(f)
            except Exception as e:
                print(f"Error scanning: {e}")

            files.sort()
            resp = json.dumps({"path": TARGET_FOLDER, "files": files})
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(resp.encode('utf-8'))
            return

        # Serve Image
        if self.path.startswith('/image/'):
            filename = urllib.parse.unquote(self.path[7:])
            filepath = os.path.join(TARGET_FOLDER, filename)
            
            if os.path.exists(filepath):
                self.send_response(200)
                mtype, _ = mimetypes.guess_type(filepath)
                self.send_header('Content-type', mtype or 'application/octet-stream')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
            return

    def do_POST(self):
        if self.path == '/api/upload':
            length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            
            files = body.get('files', [])
            target = body.get('target', 'default')
            
            print(f"🚀 Uploading {len(files)} files to /{target}...")
            
            count = 0
            for i, filename in enumerate(files):
                local = os.path.join(TARGET_FOLDER, filename)
                ext = os.path.splitext(filename)[1]
                # New name: target_1.jpg
                new_name = f"{target}_{i+1}{ext}"
                remote = f"Двухдневка в Альпы/AutoSync/{target}/{new_name}"
                
                if upload_to_bunny(local, remote):
                    print(f"✅ {filename} -> {new_name}")
                    count += 1
                else:
                    print(f"❌ Failed: {filename}")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": count}).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 photo_picker.py <FOLDER_PATH>")
        sys.exit(1)
        
    TARGET_FOLDER = sys.argv[1]
    
    if not os.path.exists(TARGET_FOLDER):
        print(f"❌ Path doesn't exist: {TARGET_FOLDER}")
        sys.exit(1)

    print(f"📂 Serving photos from: {TARGET_FOLDER}")
    print(f"🔗 OPEN THIS LINK: http://localhost:{PORT}")
    
    server = HTTPServer(('localhost', PORT), PhotoHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
