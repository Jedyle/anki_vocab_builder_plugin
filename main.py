"""
Main functionality for the Anki Language Flashcards extension.
"""

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip

from .ui.main_dialog import LanguageFlashcardsDialog


def show_language_flashcards_dialog():
    """
    Show the main dialog for creating language flashcards.
    """
    dialog = LanguageFlashcardsDialog(mw)
    dialog.exec()
