---
description: Sync best photos from Google Drive to Bunny.net
---
1. **Ensure Google Drive Files are Offline**:
   - Open Finder.
   - Navigate to `/Users/dmitry/Library/CloudStorage/GoogleDrive-kover.trips@gmail.com/Мой диск/KOVER Media Content/Автобусные туры`.
   - Right-click the folder you want to sync (e.g., `Гальштат + Зальцбург`).
   - Select **Make Available Offline**. Wait for the cloud icon to disappear/turn green.

2. **Run the Sync Script**:
   - Run the following command locally:
   ```bash
   python3 scripts/smart_upload.py "/Users/dmitry/Library/CloudStorage/GoogleDrive-kover.trips@gmail.com/Мой диск/KOVER Media Content/Автобусные туры/Гальштат + Зальцбург"
   ```
   - This script will:
     - Scan the folder.
     - Pick the top 10 largest images (best quality).
     - Upload them to Bunny.net/AutoSync.
     - Print the new public URLs.

3. **Update Website**:
   - Copy the URLs output by the script.
   - Update the HTML files (e.g., `Mobile_Version/02_Program_Mobile.html`) with the new links.
