import requests
import urllib.parse
from bs4 import BeautifulSoup
from .config import get_config


def search_images(query, language, num_images=10, provider=None):
    if not provider:
        provider = get_config().get("image_search_provider", "google")

    search_query = f"{query} {language}"

    if provider == "google":
        return _search_google_images(search_query, num_images)
    elif provider == "bing":
        return _search_bing_images(search_query, num_images)
    else:
        return _search_google_images(search_query, num_images)


def _search_google_images(query, num_images):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    escaped_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={escaped_query}&tbm=isch"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        image_elements = soup.select("img")

        image_urls = []
        for img in image_elements:
            src = img.get("src")
            if src and src.startswith("http"):
                image_urls.append(src)
            if len(image_urls) >= num_images:
                break

        return image_urls
    except Exception as e:
        print(f"Error searching Google Images: {str(e)}")
        return []


def _search_bing_images(query, num_images):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    escaped_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={escaped_query}&form=HDRSC2"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        image_elements = soup.select("img.mimg")  # Bing uses 'mimg' class for images

        image_urls = []
        for img in image_elements:
            src = img.get("src")
            if src and src.startswith("http"):
                image_urls.append(src)
            if len(image_urls) >= num_images:
                break

        return image_urls
    except Exception as e:
        print(f"Error searching Bing Images: {str(e)}")
        return []
