from PyQt5.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget
)
from handlers import ImageHandler

class ImageSelectorWidget(QWidget):
    def __init__(self, viewer, imhandler: "ImageHandler"):
        super().__init__()
        self.viewer = viewer
        self.imhandler = imhandler
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.build_layout()

    def build_layout(self):
        self.prev_button = QPushButton("Previous Image")
        self.prev_button.clicked.connect(self.on_prev_click)
        self.layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next Image")
        self.next_button.clicked.connect(self.on_next_click)
        self.layout.addWidget(self.next_button)

    def on_prev_click(self):
        self.imhandler.previous_image()

    def on_next_click(self):
        self.imhandler.next_image()
