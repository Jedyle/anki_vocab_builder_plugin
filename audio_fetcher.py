import tempfile
import requests
from urllib.request import urlopen
import os
from .config import get_config, LANGUAGE_CODES

TEMP_DIR = "/tmp"


def get_pronunciation_audio(word, language_code):
    # ex: https://ru.wiktionary.org/w/api.php?action=query&titles=%D1%82%D0%B5%D1%81%D1%82&generator=images
    url = f"https://{language_code}.wiktionary.org/w/api.php"

    params = {
        "action": "query",
        "prop": "imageinfo",
        "generator": "images",
        "titles": word,
        "format": "json",
        "iiprop": "url",
    }

    response = requests.get(url, params=params)
    data = response.json()

    audio_urls = []
    if "query" in data:
        for file_page in data["query"]["pages"].values():
            title = file_page["title"]
            if title.endswith(".ogg"):
                print("file_page", file_page)
                try:
                    audio_url = file_page["imageinfo"][0]["url"]
                    audio_urls.append(audio_url)
                except KeyError:
                    pass

    # return the first audio containing "language_code" in the title, otherwise return the first audio
    if len(audio_urls) == 0:
        return []

    # Check if any audio URL contains the language code in the title (this prevents cases where we get audio from other languages)
    for audio_url in audio_urls:
        title = audio_url.split("/")[-1]
        if title.lower().startswith(language_code):
            return audio_url
    return audio_urls[0]


def download_audio(url):
    temp_dir = os.path.join(os.getcwd(), TEMP_DIR)
    print("url", url)
    data = urlopen(url).read()
    with tempfile.NamedTemporaryFile(
        mode="wb", delete=False, suffix=".ogg", dir=temp_dir
    ) as f:
        f.write(data)
        return f


def fetch_pronunciation(word, language):
    audio_url = get_pronunciation_audio(word, language_code=LANGUAGE_CODES[language])
    audio_filename = None
    if audio_url:
        audio_filename = download_audio(audio_url).name
    return audio_filename
