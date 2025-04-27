"""
Main dialog UI for the Anki Language Flashcards extension.
"""

from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, tooltip

from ..config import get_config
from ..image_search import search_images
from ..audio_fetcher import fetch_pronunciation
from ..card_processing import process_flashcard_request
from .image_gallery import ImageGallery


class LanguageFlashcardsDialog(QDialog):
    """
    Main dialog for creating language flashcards.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.config = get_config()
        self.selected_images = []
        self.search_results = ([], None)  # Tuple of (images, audio_file)

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Language Flashcards")
        # self.setMinimumSize(800, 600)
        # a bit bigger
        self.setMinimumSize(900, 700)

        # Main layout
        layout = QVBoxLayout(self)

        # Search section
        search_group = QGroupBox("Search")
        search_layout = QGridLayout()

        # Word input
        self.word_label = QLabel("Word:")
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Enter a word in your target language")
        search_layout.addWidget(self.word_label, 0, 0)
        search_layout.addWidget(self.word_input, 0, 1)

        # Language selection
        self.language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        for lang in self.config["supported_languages"]:
            self.language_combo.addItem(lang.capitalize())

        # Set default language
        default_index = self.language_combo.findText(
            self.config["default_language"].capitalize()
        )
        if default_index >= 0:
            self.language_combo.setCurrentIndex(default_index)

        search_layout.addWidget(self.language_label, 1, 0)
        search_layout.addWidget(self.language_combo, 1, 1)

        # Search provider selection
        self.provider_label = QLabel("Search Provider:")
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("Google")
        self.provider_combo.addItem("Bing")

        # Set default provider
        default_provider = self.config["image_search_provider"].capitalize()
        default_provider_index = self.provider_combo.findText(default_provider)
        if default_provider_index >= 0:
            self.provider_combo.setCurrentIndex(default_provider_index)

        search_layout.addWidget(self.provider_label, 2, 0)
        search_layout.addWidget(self.provider_combo, 2, 1)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.on_search)
        search_layout.addWidget(
            self.search_button, 3, 1, 1, 1, Qt.AlignmentFlag.AlignRight
        )

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Audio section, displays audio when available
        # The gallery should display audio file and it should be able to click to play it

        # Audio section
        self.audio_group = QGroupBox("Pronunciation")
        audio_layout = QVBoxLayout()

        self.audio_play_button = QPushButton("Play Pronunciation")
        self.audio_play_button.setEnabled(False)  # Disabled until audio is available
        self.audio_play_button.clicked.connect(self.play_audio)

        audio_layout.addWidget(self.audio_play_button)
        self.audio_group.setLayout(audio_layout)
        layout.addWidget(self.audio_group)

        # Image gallery
        self.gallery_group = QGroupBox("Select Images")
        gallery_layout = QVBoxLayout()

        self.image_gallery = ImageGallery(self)
        self.image_gallery.selection_changed.connect(self.on_image_selection_changed)

        gallery_layout.addWidget(self.image_gallery)
        self.gallery_group.setLayout(gallery_layout)
        layout.addWidget(self.gallery_group)

        # Options section
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        # Additional text for front
        self.additional_text_label = QLabel("Additional text with image:")
        self.additional_text_input = QLineEdit()
        self.additional_text_input.setPlaceholderText("Optional additional text")
        options_layout.addWidget(self.additional_text_label)
        options_layout.addWidget(self.additional_text_input)

        # Additional text for back
        self.additional_text_back_label = QLabel("Additional text with word/audio:")
        self.additional_text_back_input = QLineEdit()
        self.additional_text_back_input.setPlaceholderText("Optional additional text")
        options_layout.addWidget(self.additional_text_back_label)
        options_layout.addWidget(self.additional_text_back_input)

        # Create reversed cards option
        self.reversed_checkbox = QCheckBox("Create reversed card (word -> image)")
        self.reversed_checkbox.setChecked(self.config["create_reversed_cards"])
        options_layout.addWidget(self.reversed_checkbox)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.create_button = QPushButton("Create Card")
        self.create_button.clicked.connect(self.on_create)
        self.create_button.setEnabled(False)  # Disabled until images are selected

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)

        layout.addLayout(button_layout)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply custom styling to the dialog."""
        # Use dark theme if configured
        if self.config.get("use_dark_theme", False):
            self.setStyleSheet(
                """
                QDialog { background-color: #2D2D30; color: #E1E1E1; }
                QGroupBox { border: 1px solid #3F3F46; border-radius: 4px; margin-top: 1em; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
                QLabel { color: #E1E1E1; }
                QLineEdit, QComboBox {
                    background-color: #1E1E1E;
                    color: #E1E1E1;
                    border: 1px solid #3F3F46;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #2D9CDB;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover { background-color: #2488C6; }
                QPushButton:disabled { background-color: #555555; color: #888888; }
                QCheckBox { color: #E1E1E1; }
                QCheckBox::indicator:checked { background-color: #2D9CDB; }
            """
            )
        else:
            # Light theme
            self.setStyleSheet(
                """
                QDialog { background-color: #F5F5F5; }
                QGroupBox {
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    margin-top: 1em;
                    font-weight: bold;
                }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
                QLineEdit, QComboBox {
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #2D9CDB;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                }
                QPushButton:hover { background-color: #2488C6; }
                QPushButton:disabled { background-color: #CCCCCC; }
                QCheckBox::indicator:checked { background-color: #2D9CDB; }
            """
            )

    def on_search(self):
        """Handle search button click."""
        word = self.word_input.text().strip()
        if not word:
            showInfo("Please enter a word to search for.")
            return

        language = self.language_combo.currentText().lower()
        provider = self.provider_combo.currentText().lower()

        # Show progress dialog
        progress = QProgressDialog("Searching for images...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(10)

        # Run the search in a background thread
        self.search_thread = SearchThread(word, language, provider)
        self.search_thread.progress_update.connect(progress.setValue)
        self.search_thread.search_complete.connect(self.on_search_complete)
        self.search_thread.search_error.connect(self.on_search_error)

        # Connect cancel button
        progress.canceled.connect(self.search_thread.terminate)

        # Start the thread
        self.search_thread.start()

    def on_search_complete(self, results):
        """Handle search completion."""
        self.search_results = results
        images, audio_file = results  # Unpack results

        self.image_gallery.set_images(images)

        if audio_file:
            self.audio_file = audio_file
            self.audio_play_button.setEnabled(True)
        else:
            self.audio_file = None
            self.audio_play_button.setEnabled(False)

        if not images:
            showInfo("No images found. Try different search terms or provider.")

    def play_audio(self):
        """Play the pronunciation audio."""
        if self.audio_file:
            from aqt.sound import play
            play(self.audio_file)

    def on_search_error(self, error_message):
        """Handle search error."""
        showInfo(f"Error searching for images: {error_message}")

    def on_image_selection_changed(self, selected_indices):
        """Handle image selection change."""
        self.selected_images = [self.search_results[0][i] for i in selected_indices]
        self.create_button.setEnabled(len(self.selected_images) > 0)

    def on_create(self):
        """Handle create button click."""
        word = self.word_input.text().strip()
        language = self.language_combo.currentText().lower()
        create_reversed = self.reversed_checkbox.isChecked()

        additional_text = self.additional_text_input.text().strip()
        additional_text_back = self.additional_text_back_input.text().strip()

        # Save preferences
        config = get_config()
        config["create_reversed_cards"] = create_reversed
        config["default_language"] = language
        config["image_search_provider"] = self.provider_combo.currentText().lower()
        from ..config import save_config

        save_config(config)

        # Process the flashcard request
        success = process_flashcard_request(
            word, language, self.selected_images,
            audio_file=self.audio_file, create_reversed=create_reversed,
            additional_text=additional_text,
            additional_text_back=additional_text_back,
            parent=self
        )

        if success:
            self.reset_dialog()

    def reset_dialog(self):
        """Reset the dialog to its initial state."""
        self.word_input.clear()
        self.image_gallery.clear()
        self.audio_play_button.setEnabled(False)
        self.create_button.setEnabled(False)
        self.selected_images = []
        self.search_results = ([], None)
        self.additional_text_input.clear()
        self.additional_text_back_input.clear()



class SearchThread(QThread):
    """Thread for searching images."""

    progress_update = pyqtSignal(int)
    search_complete = pyqtSignal(list)
    search_error = pyqtSignal(str)

    def __init__(self, word, language, provider):
        super().__init__()
        self.word = word
        self.language = language
        self.provider = provider

    def run(self):
        try:
            self.progress_update.emit(20)

            # Get config
            from ..config import get_config

            config = get_config()
            num_images = config.get("num_images_to_display", 9)

            # Search for images
            self.progress_update.emit(40)
            results = [
                search_images(self.word, self.language, num_images, self.provider),
                fetch_pronunciation(self.word, self.language)
            ]

            self.progress_update.emit(100)
            self.search_complete.emit(results)

        except Exception as e:
            self.search_error.emit(str(e))
