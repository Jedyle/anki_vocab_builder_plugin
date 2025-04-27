"""
Anki Language Flashcards
An extension for creating language flashcards with images and audio.
"""

import os
import sys

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip

from . import config
from .main import show_language_flashcards_dialog

# Add 'lib' folder to sys.path so Anki can find the packages
addon_path = os.path.dirname(__file__)
lib_path = os.path.join(addon_path, "lib")
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)


# Create a menu option
def init_addon():
    action = QAction("Language Flashcards", mw)
    action.triggered.connect(show_language_flashcards_dialog)
    mw.form.menuTools.addAction(action)


# Initialize the add-on
init_addon()
