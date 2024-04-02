import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import (
    QApplication,
)
from qfluentwidgets import (
    MSFluentWindow,
    FluentIcon,
)

from .config import Config
from .patcher import PatcherWidget


class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(QCoreApplication.translate("Window", "Balatro Patcher"))
        self.config = Config()
        self.addSubInterface(PatcherWidget(self), FluentIcon.APPLICATION, "Patcher")


def run():
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
