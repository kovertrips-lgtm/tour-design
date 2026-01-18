// State
let currentFolder = null;
let allFiles = []; // files in current folder
let globalSelection = new Set(); // store absolute paths
let renderIdx = 0;
const BATCH_SIZE = 50;

// Drag State
let dragSrcEl = null;

// UI Elements
const grid = document.getElementById('grid');
const sentinel = document.getElementById('sentinel');
const btnOpen = document.getElementById('btn-open');
const btnReview = document.getElementById('btn-review');
const btnBack = document.getElementById('btn-back');
const pathLabel = document.getElementById('current-path');
const countLabel = document.getElementById('selection-count');
const viewGrid = document.getElementById('view-grid');
const viewReview = document.getElementById('view-review');
const reviewGrid = document.getElementById('review-grid');
const targetInput = document.getElementById('target-folder');
const btnUpload = document.getElementById('btn-upload');

// --- INITIALIZATION ---
btnOpen.addEventListener('click', async () => {
    const path = await window.electronAPI.selectFolder();
    if (path) {
        currentFolder = path;
        pathLabel.innerText = path;
        pathLabel.title = path;
        loadFolder(path);
    }
});

btnReview.addEventListener('click', () => {
    if (globalSelection.size === 0) return alert("Select photos first!");
    switchView('review');
});

btnBack.addEventListener('click', () => {
    switchView('grid');
});

btnUpload.addEventListener('click', startUpload);
targetInput.addEventListener('input', updateUploadBtn);

// Infinite Scroll
const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
        renderNextBatch();
    }
});
observer.observe(sentinel);

// --- LOGIC ---

async function loadFolder(path) {
    // Clear Grid
    grid.innerHTML = '';
    renderIdx = 0;
    allFiles = [];

    // Fetch
    const files = await window.electronAPI.readDir(path);
    // Sort logic? Default alphabetical
    files.sort((a, b) => a.name.localeCompare(b.name));

    allFiles = files;
    renderNextBatch();
}

function renderNextBatch() {
    if (renderIdx >= allFiles.length) return;

    const limit = Math.min(renderIdx + BATCH_SIZE, allFiles.length);
    const fragment = document.createDocumentFragment();

    for (let i = renderIdx; i < limit; i++) {
        const file = allFiles[i];
        const card = createCard(file.path, file.name);
        fragment.appendChild(card);
    }

    grid.appendChild(fragment);
    renderIdx = limit;
}

function createCard(path, name, isReview = false) {
    const el = document.createElement('div');
    el.className = 'card';
    if (globalSelection.has(path)) el.classList.add('selected');

    // Lazy Image
    const img = document.createElement('img');
    img.loading = "lazy";
    img.src = `file://${path}`; // Electron file protocol
    img.onload = () => img.classList.add('loaded');
    el.appendChild(img);

    // Interaction
    if (!isReview) {
        el.addEventListener('click', () => toggleSelection(el, path));
    } else {
        // Review specific: Delete on click? Or drag
        // Let's create a remove button overlay for review
        const removeBtn = document.createElement('div');
        removeBtn.style = "position:absolute; bottom:5px; right:5px; background:red; width:20px; height:20px; border-radius:3px; cursor:pointer;";
        removeBtn.onclick = (e) => {
            e.stopPropagation();
            globalSelection.delete(path);
            el.remove();
            updateStats();
        };
        el.appendChild(removeBtn);

        // Drag Events
        el.draggable = true;
        el.addEventListener('dragstart', handleDragStart);
        el.addEventListener('dragover', handleDragOver);
        el.addEventListener('drop', handleDrop);
        el.addEventListener('dragend', handleDragEnd);
        el.dataset.path = path;
    }

    return el;
}

function toggleSelection(el, path) {
    if (globalSelection.has(path)) {
        globalSelection.delete(path);
        el.classList.remove('selected');
    } else {
        globalSelection.add(path);
        el.classList.add('selected');
    }
    updateStats();
}

function updateStats() {
    countLabel.innerText = globalSelection.size;
    updateUploadBtn();
}

function switchView(viewName) {
    if (viewName === 'review') {
        viewGrid.classList.remove('active');
        viewReview.classList.add('active');
        renderReviewGrid();
    } else {
        viewReview.classList.remove('active');
        viewGrid.classList.add('active');
        // Refresh grid selection state (in case removed in review)
        refreshGridState();
    }
}

function refreshGridState() {
    // Iterate existing DOM in main grid
    const cards = grid.children;
    for (let card of cards) {
        const img = card.querySelector('img');
        if (img) {
            // Reverse engineering path from src is messy (file://...)
            // Better to store path in dataset
            // Updated createCard to use dataset? No, let's fix that now if needed.
            // Actually, `img.src` is reliable enough or use dataset
        }
    }
    // Easiest hack: Just clear and re-render current folder window visible batch?
    // Or iterate dataset. Let's add dataset to createCard
    // RE-RENDERING whole current view is safer for consistency but loses scroll.
    // Let's assume user accepts re-rendering or just basic update
    // Update: Let's assume we re-init visible cards.
    // Actually, simple:
    grid.innerHTML = '';
    renderIdx = 0;
    renderNextBatch();
    // Re-fill to previous scroll position? Hard. 
    // Accept scroll reset for now as MVP.
}

function renderReviewGrid() {
    reviewGrid.innerHTML = '';
    globalSelection.forEach(path => {
        const card = createCard(path, "", true);
        reviewGrid.appendChild(card);
    });
}

function updateUploadBtn() {
    const hasFolder = targetInput.value.trim().length > 0;
    const hasFiles = globalSelection.size > 0;

    if (hasFolder && hasFiles) {
        btnUpload.disabled = false;
    } else {
        btnUpload.disabled = true;
    }
}

// --- DRAG AND DROP LOGIC ---
function handleDragStart(e) {
    this.style.opacity = '0.4';
    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    if (e.preventDefault) e.preventDefault();
    return false;
}

function handleDrop(e) {
    if (e.stopPropagation) e.stopPropagation();
    if (dragSrcEl !== this) {
        // Swap elements in DOM
        // Simple swap logic
        const parent = this.parentNode;
        const temp = document.createElement('div');
        parent.insertBefore(temp, this);
        parent.insertBefore(this, dragSrcEl);
        parent.insertBefore(dragSrcEl, temp);
        parent.removeChild(temp);
    }
    return false;
}

function handleDragEnd(e) {
    this.style.opacity = '1';
}

// --- UPLOAD ---
async function startUpload() {
    const folder = targetInput.value.trim();
    const items = Array.from(reviewGrid.children); // Get order from DOM
    const paths = items.map(el => el.dataset.path);

    btnUpload.innerText = "Uploading...";
    btnUpload.disabled = true;

    let success = 0;
    let errors = 0;

    for (let i = 0; i < paths.length; i++) {
        const res = await window.electronAPI.uploadFile({
            filePath: paths[i],
            targetFolder: folder,
            index: i + 1
        });

        if (res.success) success++;
        else errors++;

        btnUpload.innerText = `Uploading... ${i + 1}/${paths.length}`;
    }

    alert(`Finished!\nSuccess: ${success}\nErrors: ${errors}`);
    btnUpload.innerText = "Upload to Bunny";
    if (errors === 0) {
        globalSelection.clear();
        updateStats();
        switchView('grid');
        targetInput.value = '';
    } else {
        btnUpload.disabled = false;
    }
}
