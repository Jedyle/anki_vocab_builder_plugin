"""
Card creation functionality for Anki Language Flashcards.
"""

from aqt import mw
from anki.notes import Note
import os
import base64
import mimetypes


def create_flashcard(
    word,
    language,
    images,
    audio_file=None,
    create_reversed=True,
    additional_text="",
    additional_text_back="",
):
    """
    Create an Anki flashcard with the specified word, images, and audio.

    Args:
        word (str): The vocabulary word
        language (str): The target language
        images (list): List of image data (bytes)
        audio_file (str): Path to the audio file

    Returns:
        bool: True if the card was created successfully
    """
    try:
        # Get the current deck
        deck_id = mw.col.decks.current()["id"]

        # Get or create the model (note type)
        model = _get_or_create_model()

        # Create a new note
        note = Note(mw.col, model)

        # Handle images
        front_html = ""
        if images:
            front_html += "<div class='image-container'>"
            for image_data in images:
                mime_type = _guess_mime_type(image_data)
                if not mime_type:
                    continue

                b64_data = base64.b64encode(image_data).decode("utf-8")
                front_html += f"<img src='data:{mime_type};base64,{b64_data}' class='card-image' />"
            front_html += "</div>"

        # Handle audio
        audio_html = ""
        if audio_file and os.path.exists(audio_file):
            file_name = os.path.basename(audio_file)
            new_path = os.path.join(mw.col.media.dir(), file_name)

            # Copy the file if not already there
            if audio_file != new_path:
                import shutil

                shutil.copy2(audio_file, new_path)

            audio_html = f"[sound:{file_name}]"

        # Handle additional text
        if additional_text:
            front_html += f"<div>{additional_text}</div>"

        back_html = f"<div class='word-translation'>{word}</div>{audio_html}"

        # Handle additional text for the back
        if additional_text_back:
            back_html += f"<div>{additional_text_back}</div>"

        note.fields[0] = front_html  # Front
        note.fields[1] = back_html  # Back

        if create_reversed:
            note.fields[2] = "yes"  # This triggers creation of the second card
        else:
            note.fields[2] = ""  # Empty means no reverse card

        # Add to collection
        mw.col.add_note(note, deck_id)

        # Save
        mw.col.save()

        return True

    except Exception as e:
        print(f"Error creating flashcard: {str(e)}")
        return False


def _get_or_create_model():
    """
    Get or create the note type for language flashcards.

    Returns:
        dict: The model (note type)
    """
    from anki.models import ModelManager

    model_name = "Language Flashcard"

    model = mw.col.models.byName(model_name)
    if model:
        return model

    mm = mw.col.models
    model = mm.new(model_name)

    # Add fields: Front and Back
    for field in ["Front", "Back", "Add Reverse"]:
        fm = mm.newField(field)
        mm.addField(model, fm)

    # Card 1: Image -> Word
    t1 = mm.newTemplate("Image -> Word")
    t1["qfmt"] = "{{Front}}"
    t1["afmt"] = "{{FrontSide}}<hr id=answer>{{Back}}"
    mm.addTemplate(model, t1)

    # Card 2: Word -> Image (optional reverse)
    t2 = mm.newTemplate("Word -> Image")
    t2["qfmt"] = "{{#Add Reverse}}{{Back}}{{/Add Reverse}}"
    t2["afmt"] = "{{FrontSide}}<hr id=answer>{{Front}}"
    mm.addTemplate(model, t2)

    # Add CSS
    model[
        "css"
    ] = """
.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}

.image-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 20px;
}

.card-image {
    max-width: 150px;
    max-height: 150px;
    margin: 5px;
    border-radius: 5px;
    object-fit: contain;
}

.word-translation {
    font-size: 24px;
    margin-bottom: 10px;
}
"""

    mm.save(model)

    return model


def _guess_mime_type(image_data):
    """
    Guess the MIME type of image data.

    Args:
        image_data (bytes): The image data

    Returns:
        str: The MIME type
    """
    if image_data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif image_data.startswith(b"\xff\xd8"):
        return "image/jpeg"
    elif image_data.startswith(b"GIF87a") or image_data.startswith(b"GIF89a"):
        return "image/gif"
    elif image_data.startswith(b"RIFF") and image_data[8:12] == b"WEBP":
        return "image/webp"

    # Try fallback
    try:
        import magic

        return magic.from_buffer(image_data, mime=True)
    except ImportError:
        return "image/jpeg"
