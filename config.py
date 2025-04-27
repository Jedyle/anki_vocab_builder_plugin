"""
Configuration settings for the Anki Language Flashcards extension.
"""

# Default configuration settings
DEFAULT_CONFIG = {
    "num_images_to_display": 9,
    "image_search_provider": "bing",
    "max_image_width": 300,
    "max_image_height": 300,
    "audio_source": "wiktionary",
    "default_language": "spanish",
    "supported_languages": [
        "spanish",
        "french",
        "german",
        "italian",
        "portuguese",
        "japanese",
        "chinese",
        "russian",
        "korean",
    ],
    "create_reversed_cards": True,
    "use_dark_theme": False,
}

LANGUAGE_CODES = {
    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "japanese": "ja",
    "chinese": "zh",
    "russian": "ru",
    "korean": "ko",
}


# Function to get the configuration
def get_config():
    from aqt import mw

    config = mw.addonManager.getConfig(__name__)
    if config is None:
        config = DEFAULT_CONFIG
        mw.addonManager.writeConfig(__name__, config)
    return config


# Function to save the configuration
def save_config(config):
    from aqt import mw

    mw.addonManager.writeConfig(__name__, config)
