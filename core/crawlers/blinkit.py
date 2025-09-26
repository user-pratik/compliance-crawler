import os
import re
import requests
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

# Folder where images will be stored
TEMP_DIR = os.path.join("temp", "blinkit")
os.makedirs(TEMP_DIR, exist_ok=True)


def sanitize_filename(name: str) -> str:
    """Clean file name for saving images"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:100]


def download_image(url: str, folder: str, prefix: str):
    """Download image from URL"""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            basename = os.path.basename(urlparse(url).path)
            name, ext = os.path.splitext(basename)
            if not ext:
                ext = ".jpg"
            sanitized_name = sanitize_filename(name)
            filename = f"{prefix}_{sanitized_name}{ext}"
            filepath = os.path.join(folder, filename)
            with open(filepath, "wb") as f:
                f.write(r.content)
            return filepath
    except Exception as e:
        print(f"[WARN] Failed to download {url}: {e}")
    return None


def crawl(url: str):
    """Crawl a Blinkit product page"""
    data = {
        "url": url,
        "title": None,
        "mrp": None,
        "quantity": None,
        "manufacturer": None,
        "origin": None,
        "images": []
    }

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()

        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # Title
            try:
                title_el = page.query_selector("h1, [data-testid='product-title']")
                if title_el:
                    data["title"] = title_el.inner_text().strip()
            except:
                pass

            # Price (MRP)
            try:
                price_el = page.query_selector("span[data-testid='price'], .ProductPrice__value")
                if price_el:
                    data["mrp"] = price_el.inner_text().strip()
            except:
                pass

            # Quantity
            try:
                qty_el = page.query_selector("[data-testid='pack-size'], .PackSize, .product-qty")
                if qty_el:
                    data["quantity"] = qty_el.inner_text().strip()
                elif data["title"]:
                    match = re.search(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|pcs?|pack)',
                                      data["title"], re.IGNORECASE)
                    if match:
                        data["quantity"] = match.group(0)
            except:
                pass

            # Manufacturer / Origin (if available)
            try:
                details_section = page.query_selector_all("[data-testid='product-detail'] div")
                for d in details_section:
                    txt = d.inner_text().lower()
                    if "manufacturer" in txt:
                        data["manufacturer"] = d.inner_text().split(":")[-1].strip()
                    if "country of origin" in txt:
                        data["origin"] = d.inner_text().split(":")[-1].strip()
            except:
                pass

            # Images
            try:
                img_counter = 1
                downloaded_urls = set()
                imgs = page.query_selector_all("img")
                for img in imgs:
                    src = img.get_attribute("src")
                    if src and "http" in src and src not in downloaded_urls:
                        path = download_image(src, TEMP_DIR, f"img{img_counter}")
                        if path:
                            data["images"].append(path)
                            downloaded_urls.add(src)
                            img_counter += 1
                print(f"[DEBUG] Total images extracted: {len(data['images'])}")
            except Exception as e:
                print(f"[ERROR] Image extraction failed: {e}")

        except Exception as e:
            print(f"[ERROR] Crawl failed: {e}")

        finally:
            browser.close()

    return data
