
import http.server
import socketserver
import os
import urllib.parse
import json
import webbrowser
import threading
import sys

# --- CONFIG ---
PORT = 4444
ROOT_DIR = os.path.expanduser("~")

# --- HTML FRONTEND ---
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kover Photo Cull</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            background-color: #121212; 
            color: white; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0; display: flex; height: 100vh;
            overflow: hidden;
        }
        
        #sidebar {
            width: 260px;
            background: #1c1c1e;
            border-right: 1px solid #2c2c2e;
            display: flex; flex-direction: column;
            flex-shrink: 0;
        }
        
        .sb-title { padding: 15px; font-weight: bold; color: #888; text-transform: uppercase; font-size: 12px; }
        
        #folder-list {
            flex: 1; overflow-y: auto; padding: 10px;
        }
        
        .folder-item {
            padding: 8px 10px;
            cursor: pointer;
            border-radius: 6px;
            color: #ddd;
            font-size: 14px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            margin-bottom: 2px;
        }
        .folder-item:hover { background: #333; }
        .folder-item.active { background: #0A84FF; color: white; }
        
        #main {
            flex: 1; display: flex; flex-direction: column; overflow: hidden;
        }
        
        #toolbar {
            height: 60px;
            background: #1c1c1e;
            border-bottom: 1px solid #2c2c2e;
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 20px;
            flex-shrink: 0;
        }
        
        /* ROBUST GRID LAYOUT */
        #grid {
            flex: 1;
            overflow-y: scroll;
            padding: 20px;
            /* Standard Grid */
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            grid-auto-rows: 200px; /* FIXED ROW HEIGHT to preventing overlap */
            gap: 20px;
            align-content: start;
        }
        
        .card {
            background-color: #2c2c2e;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
            border: 3px solid transparent;
            /* Ensure card takes full cell size */
            width: 100%;
            height: 100%; 
            transition: transform 0.1s;
        }
        
        .card:hover { transform: scale(1.02); z-index: 10; }
        .card.selected { border-color: #30D158; }
        
        .card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        
        .card-name {
            position: absolute; bottom: 0; left: 0; right: 0;
            background: rgba(0,0,0,0.6);
            color: white; font-size: 10px; padding: 4px;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        
        .check-icon {
            position: absolute; top: 10px; right: 10px;
            width: 24px; height: 24px;
            background: #30D158; border-radius: 50%;
            display: none;
            align-items: center; justify-content: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.5);
            font-weight: bold; font-size: 14px;
        }
        .card.selected .check-icon { display: flex; }
        
        /* Buttons */
        button {
            background: #333; color: white; border: none; padding: 8px 12px;
            border-radius: 6px; cursor: pointer; font-size: 13px;
        }
        button.primary { background: #0A84FF; }
        button:hover { opacity: 0.9; }

    </style>
</head>
<body>

<div id="sidebar">
    <div class="sb-title">Navigation</div>
    <div style="padding: 10px; border-bottom: 1px solid #333;">
        <div style="display:flex; gap:5px;">
            <button style="flex:1" onclick="navigateTo('${HOME}')">🏠 Home</button>
            <button style="flex:1" onclick="navigateTo('/Volumes')">💾 Disks</button>
        </div>
        <button style="width:100%; margin-top:5px;" onclick="goUp()">⬆ Up One Level</button>
    </div>
    <div id="folder-list"></div>
</div>

<div id="main">
    <div id="toolbar">
        <div>
            <div id="path-disp" style="font-size:12px; color:#888; font-family:monospace;">/</div>
            <div id="folder-title" style="font-size:16px; font-weight:bold; margin-top:2px;">Root</div>
        </div>
        <div style="display:flex; align-items:center; gap:15px;">
            <span id="counter">0 Selected</span>
            <button class="primary" onclick="upload()">Example Upload</button>
        </div>
    </div>
    
    <div id="grid">
        <!-- Grid Items -->
    </div>
</div>

<script>
    const API = "http://localhost:4444/api";
    let currPath = "";
    let selected = new Set();
    
    // --- LOAD ---
    async function init() {
        navigateTo('${HOME}');
    }

    async function navigateTo(path) {
        currPath = path;
        document.getElementById('path-disp').innerText = path;
        document.getElementById('folder-title').innerText = path.split('/').pop() || 'Root';
        
        try {
            const res = await fetch(`${API}/list?path=${encodeURIComponent(path)}`);
            const data = await res.json();
            
            if (data.error) throw data.error;
            
            // Sidebar
            const sb = document.getElementById('folder-list');
            sb.innerHTML = '';
            data.dirs.forEach(d => {
                const div = document.createElement('div');
                div.className = 'folder-item';
                div.innerText = "📁 " + d.name;
                div.onclick = () => navigateTo(d.path);
                sb.appendChild(div);
            });
            
            // Grid
            const grid = document.getElementById('grid');
            grid.innerHTML = '';
            
            if (data.files.length === 0) {
                grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:50px; color:#555;">No images</div>';
                return;
            }
            
            // Use fragment
            const frag = document.createDocumentFragment();
            data.files.forEach(f => {
                const el = document.createElement('div');
                el.className = 'card';
                if (selected.has(f.path)) el.classList.add('selected');
                
                el.onclick = () => {
                    if (selected.has(f.path)) {
                        selected.delete(f.path);
                        el.classList.remove('selected');
                    } else {
                        selected.add(f.path);
                        el.classList.add('selected');
                    }
                    document.getElementById('counter').innerText = `${selected.size} Selected`;
                };
                
                el.innerHTML = `
                    <div class="check-icon">✓</div>
                    <img loading="lazy" src="${API}/image?path=${encodeURIComponent(f.path)}" />
                    <div class="card-name">${f.name}</div>
                `;
                frag.appendChild(el);
            });
            grid.appendChild(frag);
            
        } catch(e) {
            alert("Error: " + e);
        }
    }
    
    function goUp() {
        if (currPath === '/' || currPath === '/Volumes') return;
        const p = currPath.substring(0, currPath.lastIndexOf('/')) || '/';
        navigateTo(p);
    }
    
    async function upload() {
        if (selected.size === 0) return alert("Select items first");
        const name = prompt("Folder Name:");
        if(!name) return;
        
        const files = Array.from(selected);
        await fetch(`${API}/upload`, {
            method:'POST', body:JSON.stringify({folder:name, files:files})
        });
        alert("Started upload");
    }
    
    init();
</script>
</body>
</html>
""".replace("${HOME}", os.path.expanduser("~"))

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): return 
    
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
            return
            
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == "/api/list":
            path = qs.get('path', [os.path.expanduser("~")])[0]
            try:
                items = os.listdir(path)
                dirs = []
                files = []
                exts = {'.jpg','.jpeg','.png','.webp','.heic','.JPG','.PNG'}
                for x in items:
                    if x.startswith('.'): continue
                    fp = os.path.join(path, x)
                    if os.path.isdir(fp):
                        dirs.append({'name':x, 'path':fp})
                    elif os.path.isfile(fp) and os.path.splitext(x)[1] in exts:
                        files.append({'name':x, 'path':fp})
                
                dirs.sort(key=lambda x:x['name'])
                files.sort(key=lambda x:x['name'])
                
                self.send_json({'dirs':dirs, 'files':files})
            except Exception as e:
                self.send_json({'error':str(e)})
                
        elif parsed.path == "/api/image":
            path = qs.get('path',[None])[0]
            if path and os.path.exists(path):
                self.send_response(200)
                self.end_headers()
                with open(path,'rb') as f: self.wfile.write(f.read())
                
    def do_POST(self):
        if self.path == "/api/upload":
            l = int(self.headers.get('content-length'))
            d = json.loads(self.rfile.read(l))
            threading.Thread(target=self.run_up, args=(d['folder'], d['files'])).start()
            self.send_response(200)
            self.end_headers()
            
    def run_up(self, folder, files):
        import urllib.request
        BUNNY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
        for i, fp in enumerate(files):
            try:
                fn = os.path.basename(fp)
                rem = f"Двухдневка в Альпы/AutoSync/{folder}/{fn}"
                s_rem = urllib.parse.quote(rem)
                # Note: BunnyCDN expects full path in URL, carefully encoded
                # Fix: double encoding sometimes needed or treating / specially
                # Simple fix: split by / and encode parts
                
                # Correct Logic for Bunny Path
                path_parts = rem.split('/') 
                safe_path = "/".join(urllib.parse.quote(part) for part in path_parts)
                
                url = f"https://storage.bunnycdn.com/kovertripweb/{safe_path}"
                
                with open(fp,'rb') as f:
                    req = urllib.request.Request(url, data=f.read(), method="PUT")
                    req.add_header('AccessKey', BUNNY)
                    urllib.request.urlopen(req)
                print(f"Uploaded {fn}")
            except Exception as e: print(e)

    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d).encode('utf-8'))

try:
    s = http.server.HTTPServer(("", PORT), Handler)
    print(f"Serving on {PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    s.serve_forever()
except:
    webbrowser.open(f"http://localhost:{PORT}")
