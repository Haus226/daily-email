import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://commons.wikimedia.org"
CATEGORY_URL = f"{BASE_URL}/wiki/Category:The_Pictorial_Key_to_the_Tarot"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_image_page_links(category_url):
    print("🔍 Fetching gallery links...")
    res = requests.get(category_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    gallery_links = soup.find_all("a", href=True, class_="mw-file-description")
    return [BASE_URL + a["href"] for a in gallery_links]

def get_image_url(image_page_url):
    print(f"📄 Fetching image URL from {image_page_url}")
    res = requests.get(image_page_url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    full_image = soup.select_one("div.fullImageLink a")
    return full_image["href"] if full_image else None

def download_image(image_url, save_dir="tarot_cards"):
    os.makedirs(save_dir, exist_ok=True)
    file_name = os.path.basename(image_url)
    file_path = os.path.join(save_dir, file_name)
    print(f"⬇️ Downloading {file_name} ...")
    img_data = requests.get(image_url, headers=HEADERS).content
    with open(file_path, "wb") as f:
        f.write(img_data)
    return file_path

def scrape_tarot_cards():
    image_page_links = get_image_page_links(CATEGORY_URL)
    for link in image_page_links:
        try:
            image_url = get_image_url(link)
            if image_url:
                download_image(image_url)
                time.sleep(1)  # polite delay
        except Exception as e:
            print(f"❌ Failed for {link}: {e}")

if __name__ == "__main__":
    scrape_tarot_cards()
