"""
Card processing functionality for the Anki Language Flashcards extension.
"""

from aqt.qt import *
from aqt.utils import showInfo, tooltip

from .image_search import search_images
from .audio_fetcher import fetch_pronunciation
from .card_creator import create_flashcard


def process_flashcard_request(
    word,
    language,
    selected_images,
    audio_file=None,
    create_reversed=True,
    additional_text="",
    additional_text_back="",
    parent=None,
):
    """
    Process a flashcard creation request.

    Args:
        word (str): The vocabulary word
        language (str): The target language
        selected_images (list): List of selected image URLs
        parent (QWidget): Parent widget for progress dialogs

    Returns:
        bool: True if card was created successfully
    """
    # Show progress dialog
    progress = QProgressDialog("Creating flashcard...", "Cancel", 0, 3, parent)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.setMinimumDuration(0)
    progress.setValue(0)

    try:
        # Step 1: Download selected images
        progress.setLabelText("Downloading selected images...")
        progress.setValue(1)
        QApplication.processEvents()

        downloaded_images = []
        for url in selected_images:
            image_data = download_image(url)
            if image_data:
                downloaded_images.append(image_data)

        if progress.wasCanceled():
            return False

        # Step 2: Create the flashcard
        progress.setLabelText("Creating Anki card...")
        progress.setValue(3)
        QApplication.processEvents()

        success = create_flashcard(
            word,
            language,
            downloaded_images,
            audio_file,
            create_reversed,
            additional_text,
            additional_text_back,
        )

        if success:
            tooltip("Flashcard created successfully!", parent=parent)
            return True
        else:
            showInfo("Failed to create flashcard.", parent=parent)
            return False

    except Exception as e:
        showInfo(f"Error creating flashcard: {str(e)}", parent=parent)
        return False
    finally:
        progress.setValue(3)


def download_image(url):
    """
    Download an image from a URL.

    Args:
        url (str): The image URL

    Returns:
        bytes: The image data
    """
    import requests

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
        return None
    except Exception:
        return None
