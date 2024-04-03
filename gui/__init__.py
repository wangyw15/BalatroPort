import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QTranslator, QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
)
from qfluentwidgets import (
    MSFluentWindow,
    FluentIcon,
)

from .config import Config
from .patcher import PatcherWidget
from libs import feature


class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(str(Path(__file__).parent.parent / "icon.ico")))
        self.setWindowTitle(QCoreApplication.translate("Window", "Balatro Patcher"))
        self.resize(600, 400)
        self.config = Config()
        self.addSubInterface(
            PatcherWidget(self),
            FluentIcon.APPLICATION,
            QCoreApplication.translate("Window", "Patcher"),
        )
        if feature.apk_packer_enabled():
            from .apk_packer import ApkPackerWidget
            self.addSubInterface(
                ApkPackerWidget(self),
                FluentIcon.SAVE,
                QCoreApplication.translate("Window", "ApkPacker"),
            )


def run():
    i18n_dir = Path(__file__).parent.parent / "i18n"
    app = QApplication([])

    # language translation
    translator = QTranslator()
    if translator.load(f"{QLocale.system().name()}.qm", directory=str(i18n_dir)):
        app.installTranslator(translator)

    window = Window()
    window.show()
    sys.exit(app.exec())
