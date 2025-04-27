"""
Image gallery widget for the Anki Language Flashcards extension.
"""

from aqt.qt import *
import requests
from threading import Thread
from queue import Queue
import time


class ImageGallery(QWidget):
    """
    Widget for displaying and selecting images.
    """

    selection_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.images = []
        self.thumbnails = {}
        self.selected_indices = set()

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create scroll area
        scroll_area = QScrollArea()
        # min height
        scroll_area.setMinimumHeight(300)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)

        # Set up grid layout properties
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)

        # Add container to scroll area
        scroll_area.setWidget(self.container)
        layout.addWidget(scroll_area)

        # Status label
        self.status_label = QLabel("No images found")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Set up placeholder widgets
        self.placeholder_widgets = []

    def set_images(self, image_urls):
        """
        Set the images to display in the gallery.

        Args:
            image_urls (list): List of image URLs
        """
        # Clear previous images
        self.clear()

        # Store new image URLs
        self.images = image_urls

        if not image_urls:
            self.status_label.setText("No images found")
            return

        # Update status
        self.status_label.setText(f"Loading {len(image_urls)} images...")

        # Calculate grid dimensions
        num_images = len(image_urls)
        cols = min(3, num_images)
        rows = (num_images + cols - 1) // cols  # Ceiling division

        # Create placeholder widgets
        for i in range(num_images):
            row = i // cols
            col = i % cols

            # Create image container
            container = QFrame()
            container.setFrameShape(QFrame.Shape.StyledPanel)
            container.setFrameShadow(QFrame.Shadow.Raised)
            container.setMinimumSize(200, 200)
            container.setMaximumSize(250, 250)
            container.setStyleSheet(
                """
                QFrame {
                    background-color: #F0F0F0;
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                }
                QFrame[selected="true"] {
                    border: 3px solid #2D9CDB;
                }
            """
            )
            container.setProperty("selected", "false")

            # Create layout for container
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)

            # Create label for image
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            image_label.setScaledContents(False)
            image_label.setText("Loading...")

            container_layout.addWidget(image_label)

            # Add to grid
            self.grid_layout.addWidget(container, row, col)

            # Store placeholder widgets
            self.placeholder_widgets.append((container, image_label, i))

            # Set up click event
            container.mousePressEvent = lambda event, idx=i: self.toggle_selection(idx)

        # Load images in background
        self.load_images_thread()

    def load_images_thread(self):
        """Load images in a background thread."""
        # Create queue for loading images
        self.image_queue = Queue()
        for i, url in enumerate(self.images):
            self.image_queue.put((i, url))

        # Create download threads
        num_threads = min(4, len(self.images))
        self.download_threads = []

        for _ in range(num_threads):
            thread = Thread(target=self.download_worker)
            thread.daemon = True
            thread.start()
            self.download_threads.append(thread)

    def download_worker(self):
        """Worker function to download images."""
        while not self.image_queue.empty():
            try:
                i, url = self.image_queue.get(timeout=0.1)
            except:
                break

            try:
                # Download image
                response = requests.get(url, timeout=10)
                image_data = response.content

                # Create QImage from data
                image = QImage.fromData(image_data)

                if not image.isNull():
                    # Create pixmap
                    pixmap = QPixmap.fromImage(image)

                    # Scale pixmap
                    scaled_pixmap = pixmap.scaled(
                        150,
                        150,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )

                    # Store thumbnail
                    self.thumbnails[i] = scaled_pixmap

                    # Update UI in main thread
                    QMetaObject.invokeMethod(
                        self,
                        "update_thumbnail",
                        Qt.ConnectionType.QueuedConnection,
                        Q_ARG(int, i),
                        Q_ARG(object, scaled_pixmap),
                    )
            except Exception as e:
                print(f"Error downloading image {url}: {str(e)}")

            # Mark task as completed
            self.image_queue.task_done()

        # If this is the last thread to finish, update status
        if self.image_queue.qsize() == 0:
            QMetaObject.invokeMethod(
                self,
                "update_status",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, f"Found {len(self.thumbnails)} images"),
            )

    @pyqtSlot(int, object)
    def update_thumbnail(self, index, pixmap):
        """
        Update the thumbnail for an image.

        Args:
            index (int): The image index
            pixmap (QPixmap): The thumbnail pixmap
        """
        # Find the label for this index
        for container, label, i in self.placeholder_widgets:
            if i == index:
                label.setPixmap(pixmap)
                label.setText("")
                break

    @pyqtSlot(str)
    def update_status(self, text):
        """
        Update the status label.

        Args:
            text (str): The new status text
        """
        self.status_label.setText(text)

    def toggle_selection(self, index):
        """
        Toggle selection for an image.

        Args:
            index (int): The image index
        """
        # Find container for this index
        container = None
        for c, _, i in self.placeholder_widgets:
            if i == index:
                container = c
                break

        if not container:
            return

        # Toggle selection
        if index in self.selected_indices:
            self.selected_indices.remove(index)
            container.setProperty("selected", "false")
        else:
            self.selected_indices.add(index)
            container.setProperty("selected", "true")

        # Update style
        container.style().unpolish(container)
        container.style().polish(container)

        # Emit signal
        self.selection_changed.emit(list(self.selected_indices))

    def clear(self):
        """Clear the gallery."""
        # Remove all widgets from grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear data
        self.images = []
        self.thumbnails = {}
        self.selected_indices = set()
        self.placeholder_widgets = []

        # Update status
        self.status_label.setText("No images found")
