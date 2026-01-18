
import requests

API_KEY = "362d59db-046b-4538-821bf3d1d197-7ea2-42f4"
STORAGE_ZONE_NAME = "kovertripweb"
BASE_URL = "https://storage.bunnycdn.com"

def list_files(path):
    headers = {"AccessKey": API_KEY}
    url = f"{BASE_URL}/{STORAGE_ZONE_NAME}/{path}/"
    print(f"Checking: {url}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("Found files/folders:")
        for item in response.json():
            print(f"- {item['ObjectName']} ({('DIR' if item['IsDirectory'] else 'FILE')})")
    else:
        print(f"Error: {response.status_code} - {response.text}")

list_files("Двухдневка в Альпы")
