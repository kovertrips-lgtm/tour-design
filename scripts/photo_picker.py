
import os
import sys
import json
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import mimetypes
import webbrowser

# --- CONFIG ---
BUNNY_API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_NAME = "kovertripweb"
PORT = 8000
TARGET_FOLDER = ""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Photo Picker (Fast)</title>
    <meta charset="utf-8">
    <style>
        body { background: #111; color: white; font-family: sans-serif; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px; margin-top:20px;}
        .card { position: relative; aspect-ratio: 1; background: #222; overflow: hidden; cursor: pointer; border: 2px solid transparent; transition: border 0.1s; }
        .card:hover { border-color: #555; }
        .card.selected { border-color: lime; box-shadow: 0 0 10px rgba(0,255,0,0.3); }
        
        img { width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 0.3s; }
        img.loaded { opacity: 1; }
        
        /* Bar Styles */
        .bar { position: sticky; top: 0; background: #111; padding: 10px; border-bottom: 1px solid #333; display: flex; gap: 10px; z-index: 10; align-items: center;}
        
        button { padding: 8px 15px; cursor: pointer; border-radius: 5px; border: none; font-weight: bold;}
        .btn-upload { background: #00bfff; color: white; }
        .btn-reset { background: #444; color: white; }
        
        .path { font-size: 12px; color: #888; }
        
        /* Review specific */
        #review-grid .card { cursor: default; }
        #review-grid .card:hover { border-color: red; }
    </style>
</head>
<body>
    <div class="bar">
        <div>
            <div style="font-weight:bold;">📸 Photo Picker</div>
            <div class="path" id="path-str">Loading...</div>
        </div>
        <div style="flex-grow:1"></div>
        
        <input type="text" id="bucket-folder" placeholder="Folder Name (e.g. hotel_spa)" style="padding:8px; border-radius:4px; border:1px solid #444; background:#222; color:white; width: 200px;">
        
        <!-- Main Controls -->
        <span id="main-controls">
            <button class="btn-reset" onclick="reset()">Reset</button>
            <button class="btn-upload" onclick="startReview()" id="btn-review" disabled style="opacity:0.5; cursor:not-allowed">Review (0)</button>
        </span>

        <!-- Review Controls -->
        <span id="review-controls" style="display:none">
            <button class="btn-reset" onclick="cancelReview()">⬅️ Edit</button>
            <button class="btn-upload" onclick="confirmUpload()" id="btn-confirm" style="background:#00eb00; color:black">✅ Confirm Upload</button>
        </span>
    </div>

    <div id="main-view">
        <div class="grid" id="grid"></div>
        <div id="loader-trigger" style="height:50px; text-align:center; padding:20px; color:#555;">Thinking...</div>
    </div>
    
    <!-- Review View (Keep same) -->
    <div id="review-view" style="display:none">
        <h2 style="text-align:center; color:#ccc;">Review Selection</h2>
        <div style="text-align:center; color:#666; font-size:12px; margin-bottom:10px;">Click image to remove from selection</div>
        <div class="grid" id="review-grid"></div>
    </div>

    <script>
        let selected = new Set();
        let allItems = [];
        let renderIdx = 0;
        const BATCH = 32;
        
        // UI Refs
        const folderInput = document.getElementById('bucket-folder');
        const reviewBtn = document.getElementById('btn-review');
        const grid = document.getElementById('grid');
        const loader = document.getElementById('loader-trigger');

        // Validation
        folderInput.addEventListener('input', updateBtn);

        // Infinite Scroll Observer
        const observer = new IntersectionObserver((entries) => {
            if(entries[0].isIntersecting) {
                renderNextBatch();
            }
        });
        observer.observe(loader);

        async function init(path = "") {
            try {
                // Reset State
                allItems = [];
                renderIdx = 0;
                grid.innerHTML = '';
                loader.innerText = 'Loading list...';
                
                const url = path ? `/api/files?path=${encodeURIComponent(path)}` : '/api/files';
                const res = await fetch(url);
                const data = await res.json();
                
                if(data.error) return; 
                
                document.getElementById('path-str').innerText = data.path;
                
                // Separate Dirs and Files
                const dirs = data.items.filter(i => i.type === 'dir');
                const files = data.items.filter(i => i.type === 'file');
                
                // We always render directories first, immediately
                dirs.forEach(item => {
                    const el = document.createElement('div');
                    el.className = 'card';
                    el.style.background = item.is_back ? '#333' : '#2A2A2A';
                    el.style.display = 'flex';
                    el.style.alignItems = 'center';
                    el.style.justifyContent = 'center';
                    el.style.flexDirection = 'column';
                    el.style.border = '1px dashed #444';
                    el.innerHTML = `<div style="font-size:40px">${item.is_back ? '⬆️' : '📁'}</div><div style="font-size:12px; padding:5px; text-align:center">${item.name}</div>`;
                    el.onclick = () => init(item.path);
                    grid.appendChild(el);
                });

                // Store files for lazy rendering
                allItems = files;
                if (allItems.length === 0 && dirs.length === 0) {
                     loader.innerText = 'Empty folder';
                } else {
                     loader.innerText = 'Scroll for more...';
                     renderNextBatch(); // Render first batch
                }

            } catch(e) { console.error(e); }
        }

        function renderNextBatch() {
            if (renderIdx >= allItems.length) {
                if(allItems.length > 0) loader.innerText = "End of list";
                return;
            }
            
            const limit = Math.min(renderIdx + BATCH, allItems.length);
            
            for (let i = renderIdx; i < limit; i++) {
                const item = allItems[i];
                const el = document.createElement('div');
                el.className = 'card';
                if(selected.has(item.path)) el.classList.add('selected');
                
                el.onclick = () => toggle(el, item.path);
                
                // Lazy load image src only when created
                el.innerHTML = `<img src="/img/${encodeURIComponent(item.path)}" loading="lazy">`;
                grid.appendChild(el);
            }
            
            renderIdx = limit;
        }

        function toggle(el, full_path) {
            if(selected.has(full_path)) {
                selected.delete(full_path);
                el.classList.remove('selected');
            } else {
                selected.add(full_path);
                el.classList.add('selected');
            }
            updateBtn();
        }
        
        function reset() {
            selected.clear();
            document.querySelectorAll('.selected').forEach(e => e.classList.remove('selected'));
            updateBtn();
        }

        // ... updateBtn, startReview, renderReviewGrid, cancelReview, confirmUpload SAME AS BEFORE ...
        function updateBtn() {
            const hasFolder = folderInput.value.trim().length > 0;
            const hasFiles = selected.size > 0;
            
            reviewBtn.innerText = `Review (${selected.size})`;
            
            if (hasFolder && hasFiles) {
                reviewBtn.disabled = false;
                reviewBtn.style.opacity = '1';
                reviewBtn.style.cursor = 'pointer';
            } else {
                reviewBtn.disabled = true;
                reviewBtn.style.opacity = '0.5';
                reviewBtn.style.cursor = 'not-allowed';
            }
        }

        function startReview() {
            document.getElementById('main-view').style.display = 'none';
            document.getElementById('review-view').style.display = 'block';
            document.getElementById('main-controls').style.display = 'none';
            document.getElementById('review-controls').style.display = 'inline-block';
            folderInput.disabled = true;
            renderReviewGrid();
        }

        function renderReviewGrid() {
            const rGrid = document.getElementById('review-grid');
            rGrid.innerHTML = '';
            selected.forEach(path => {
                const el = document.createElement('div');
                el.className = 'card selected';
                el.onclick = () => {
                    selected.delete(path);
                    renderReviewGrid();
                    updateBtn();
                    if(selected.size === 0) cancelReview();
                };
                el.innerHTML = `<img src="/img/${encodeURIComponent(path)}" loading="lazy"><div style="position:absolute; bottom:0; padding:5px; background:rgba(0,0,0,0.5); width:100%; font-size:10px; color:white; text-align:center">🗑 Remove</div>`;
                rGrid.appendChild(el);
            });
        }

        function cancelReview() {
            document.getElementById('main-view').style.display = 'block';
            document.getElementById('review-view').style.display = 'none';
            document.getElementById('main-controls').style.display = 'inline-block';
            document.getElementById('review-controls').style.display = 'none';
            folderInput.disabled = false;
            // Note: We don't re-init here to preserve scroll, but simple implementation is re-init
            // The user might lose position, but it ensures consistency.
            // Optimized: Just show main view. DOM is preserved!
        }

        async function confirmUpload() {
            const folder = folderInput.value.trim();
            if(!folder) return alert("Folder name required");
            const btn = document.getElementById('btn-confirm');
            btn.innerText = "Uploading...";
            btn.disabled = true;
            try {
                const res = await fetch('/api/upload', {
                    method: 'POST',
                    body: JSON.stringify({
                        files: Array.from(selected),
                        target: folder
                    })
                });
                const j = await res.json();
                
                if(j.errors && j.errors.length > 0) {
                     alert(`⚠️ Finished with errors.\nSuccess: ${j.count}\nFailed: ${j.errors.join(', ')}`);
                } else {
                     alert("🚀 Uploaded " + (j.count || 0) + " files!");
                }
                
                selected.clear();
                cancelReview(); 
                reset();
            } catch(e) {
                alert("Error: " + e);
            }
            btn.disabled = false;
            btn.innerText = "✅ Confirm Upload";
            updateBtn();
        }

        init();
    </script>
</body>
</html>
"""

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
                return
            
            # API: LIST FILES
            if self.path.startswith('/api/files'):
                query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                current_dir = query.get('path', [TARGET_FOLDER])[0]
                
                if not os.path.exists(current_dir):
                     current_dir = TARGET_FOLDER

                parent_dir = os.path.dirname(current_dir)

                items = []
                if len(parent_dir) > 5:
                     items.append({"name": "⬅️ НАЗАД", "path": parent_dir, "type": "dir", "is_back": True})

                try:
                    raw_items = os.listdir(current_dir)
                    raw_items.sort()
                    
                    for f in raw_items:
                        full = os.path.join(current_dir, f)
                        if f.startswith('.'): continue
                        
                        if os.path.isdir(full):
                            items.append({"name": f, "path": full, "type": "dir"})
                        elif f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            items.append({"name": f, "path": full, "type": "file"})
                except Exception as e:
                    pass 
                
                data = {"path": current_dir, "items": items}
                self.send_json(data)
                return

            # API: SERVE IMAGE
            if self.path.startswith('/img/'):
                fpath = urllib.parse.unquote(self.path[5:])
                if os.path.exists(fpath):
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    # Aggressive Caching for Speed
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    self.end_headers()
                    try:
                        with open(fpath, 'rb') as f:
                            self.wfile.write(f.read())
                    except BrokenPipeError:
                        pass
                else:
                    self.send_error(404)
                return
        except Exception as e:
            print(f"Error: {e}")

    def do_POST(self):
        if self.path == '/api/upload':
            try:
                length = int(self.headers['Content-Length'])
                # READ and DECODE explicitly
                payload = self.rfile.read(length).decode('utf-8')
                body = json.loads(payload)
                
                target_bucket = body.get('target', 'default')
                files_to_up = body.get('files', [])
                
                print(f"🚀 Starting upload of {len(files_to_up)} files to '{target_bucket}'")
                
                count = 0
                errors = []
                for i, fname in enumerate(files_to_up):
                    local_p = fname 
                    ext = os.path.splitext(fname)[1]
                    new_name = f"{target_bucket}_{i+1}{ext}"
                    remote_p = f"Двухдневка в Альпы/AutoSync/{target_bucket}/{new_name}"
                    
                    print(f"   Uploading: {os.path.basename(local_p)} -> {new_name}")
                    
                    if self.upload_bunny(local_p, remote_p):
                        count += 1
                    else:
                        print(f"   ❌ FAILED: {local_p}")
                        errors.append(os.path.basename(local_p))
                
                print(f"✅ Finished: {count} success, {len(errors)} errors")
                self.send_json({"count": count, "errors": errors})
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_json({"error": str(e), "details": traceback.format_exc()})

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def upload_bunny(self, local, remote):
        safe_remote = "/".join([urllib.parse.quote(p) for p in remote.split('/')])
        url = f"https://storage.bunnycdn.com/{STORAGE_NAME}/{safe_remote}"
        headers = {"AccessKey": BUNNY_API_KEY, "Content-Type": "application/octet-stream"}
        try:
            req = urllib.request.Request(url, data=open(local, "rb").read(), headers=headers, method='PUT')
            with urllib.request.urlopen(req) as res:
                return res.status == 201
        except Exception as e:
            print(f"Err: {e}")
            return False

# MULTI-THREADED SERVER for fast loading
class ThreadedServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        TARGET_FOLDER = sys.argv[1]
    else:
        print("Need path arg")
        sys.exit(1)
        
    print(f"Serving: {TARGET_FOLDER}")
    # Kill old
    os.system(f"lsof -ti:{PORT} | xargs kill -9 2>/dev/null")
    
    server = ThreadedServer(('localhost', PORT), SimpleHandler)
    webbrowser.open(f"http://localhost:{PORT}")
    try:
        server.serve_forever()
    except:
        pass
