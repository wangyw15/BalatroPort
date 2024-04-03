from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import (
    QGridLayout,
    QFileDialog,
    QMessageBox,
    QWidget,
)
from qfluentwidgets import (
    PushButton,
    LineEdit,
    StrongBodyLabel,
    InfoBarIcon,
    TeachingTip,
)

import android_packer


class ApkPackerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ApkPacker")

        self.layout = QGridLayout(self)
        self.edit_game_path = LineEdit(self)
        self.button_browse_game = PushButton(
            QCoreApplication.translate("ApkPacker", "Browse"), self
        )
        self.edit_save_path = LineEdit(self)
        self.button_browse_save = PushButton(
            QCoreApplication.translate("ApkPacker", "Browse"), self
        )
        self.button_pack = PushButton(
            QCoreApplication.translate(
                "ApkPacker", "Pack (need some time, please wait)"
            ),
            self,
        )

        self.layout.addWidget(
            StrongBodyLabel(
                QCoreApplication.translate(
                    "ApkPacker", "Path to packed game (game.love)"
                ),
                self,
            ),
            0,
            0,
            1,
            3,
        )
        self.layout.addWidget(self.edit_game_path, 1, 0, 1, 2)
        self.layout.addWidget(self.button_browse_game, 1, 2)
        self.layout.addWidget(
            StrongBodyLabel(
                QCoreApplication.translate("ApkPacker", "Save apk path"), self
            ),
            2,
            0,
            1,
            3,
        )
        self.layout.addWidget(self.edit_save_path, 3, 0, 1, 2)
        self.layout.addWidget(self.button_browse_save, 3, 2)
        self.layout.addWidget(self.button_pack, 4, 0, 1, 3)

        self.button_browse_game.clicked.connect(self.browse_game)
        self.button_browse_save.clicked.connect(self.browse_save)
        self.button_pack.clicked.connect(self.pack_apk)

    def browse_game(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter(
            "game.love (*.love *.zip);;"
            f'{QCoreApplication.translate("ApkPacker", "All files")} (*.*)'
        )
        if file_dialog.exec():
            self.edit_game_path.setText(file_dialog.selectedFiles()[0])

    def browse_save(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setNameFilter(
            f'{QCoreApplication.translate("ApkPacker", "APK file")}  (*.apk);;'
            f'{QCoreApplication.translate("ApkPacker", "All files")} (*.*)'
        )
        file_dialog.setDefaultSuffix("apk")
        if file_dialog.exec():
            self.edit_save_path.setText(file_dialog.selectedFiles()[0])

    def pack_apk(self):
        self.button_pack.setEnabled(False)

        if not self.edit_game_path.text():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title=QCoreApplication.translate("ApkPacker", "No file selected"),
                content=QCoreApplication.translate(
                    "ApkPacker", "No game.love selected."
                ),
                target=self.edit_game_path,
                parent=self,
                isClosable=True,
            )
            return
        if not self.edit_save_path.text():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title=QCoreApplication.translate("ApkPacker", "No file selected"),
                content=QCoreApplication.translate(
                    "ApkPacker", "No save path selected."
                ),
                target=self.edit_save_path,
                parent=self,
                isClosable=True,
            )
            return

        game_path = Path(self.edit_game_path.text())
        save_path = Path(self.edit_save_path.text())

        if not game_path.exists():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title=QCoreApplication.translate("ApkPacker", "File not found"),
                content=QCoreApplication.translate(
                    "ApkPacker", "Selected game.love not found."
                ),
                target=self.edit_game_path,
                parent=self,
                isClosable=True,
            )
            return

        with game_path.open("rb") as f:
            android_packer.pack_game_apk(f.read(), save_path)

        self.button_pack.setEnabled(True)
        TeachingTip.create(
            icon=InfoBarIcon.SUCCESS,
            title=QCoreApplication.translate("ApkPacker", "Success"),
            content=QCoreApplication.translate("ApkPacker", "Packing complete."),
            target=self.button_pack,
            parent=self,
            isClosable=True,
        )
