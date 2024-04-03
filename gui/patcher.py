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
    CheckBox,
    LineEdit,
    StrongBodyLabel,
    FluentIcon,
    InfoBarIcon,
    TeachingTip,
    OptionsSettingCard,
)

import patchers
from libs import love2d_helper
from .config import Config


class PatcherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Patcher")
        if "config" in parent.__dict__:
            self.config: Config = parent.__dict__["config"]
        else:
            self.config: Config = Config()

        # widgets
        self.layout = QGridLayout(self)
        self.edit_executable_path = LineEdit(self)
        self.button_browse_executable = PushButton(
            QCoreApplication.translate("Patcher", "Browse"), self
        )
        self.edit_save_path = LineEdit(self)
        self.button_browse_save = PushButton(
            QCoreApplication.translate("Patcher", "Browse"), self
        )
        self.options_card_output_type = OptionsSettingCard(
            icon=FluentIcon.SAVE,
            configItem=self.config.outputType,
            title=QCoreApplication.translate("Patcher", "Output type"),
            content=QCoreApplication.translate(
                "Patcher", "Select the type of output file you want to generate."
            ),
            texts=love2d_helper.VALID_OUTPUT_TYPES,
        )
        self.button_patch = PushButton(
            QCoreApplication.translate("Patcher", "Patch"), self
        )
        self.checkbox_patchers = []

        # layout
        for i, patcher_name in enumerate(patchers.get_patcher_names()):
            self.checkbox_patchers.append(CheckBox(patcher_name, self))
            self.layout.addWidget(self.checkbox_patchers[i], 1, i)

        self.layout.addWidget(
            StrongBodyLabel(
                QCoreApplication.translate("Patcher", "Select patchers"), self
            ),
            0,
            0,
            1,
            self.layout.columnCount(),
        )
        self.layout.addWidget(
            StrongBodyLabel(
                QCoreApplication.translate("Patcher", "Select Balatro.exe"), self
            ),
            2,
            0,
            1,
            self.layout.columnCount(),
        )
        self.layout.addWidget(
            self.edit_executable_path, 3, 0, 1, self.layout.columnCount() - 1
        )
        self.layout.addWidget(
            self.button_browse_executable, 3, self.layout.columnCount() - 1
        )
        self.layout.addWidget(
            StrongBodyLabel(
                QCoreApplication.translate("Patcher", "Path to save"), self
            ),
            4,
            0,
            1,
            self.layout.columnCount(),
        )
        self.layout.addWidget(
            self.edit_save_path, 5, 0, 1, self.layout.columnCount() - 1
        )
        self.layout.addWidget(self.button_browse_save, 5, self.layout.columnCount() - 1)
        self.layout.addWidget(
            self.options_card_output_type, 6, 0, 1, self.layout.columnCount()
        )
        self.layout.addWidget(self.button_patch, 7, 0, 1, self.layout.columnCount())

        # signals
        self.button_browse_executable.clicked.connect(self.browse_executable)
        self.button_browse_save.clicked.connect(self.browse_save)
        self.button_patch.clicked.connect(self.patch_game)

    def browse_executable(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter(
            f'{QCoreApplication.translate("Patcher", "Balatro executable")} (*.exe)'
        )
        if file_dialog.exec():
            self.edit_executable_path.setText(file_dialog.selectedFiles()[0])

    def browse_save(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setNameFilter(
            f'{QCoreApplication.translate("Patcher", "Balatro executable")}  (*.exe);;'
            f'{QCoreApplication.translate("Patcher", "Game only")} (*.love);;'
            f'{QCoreApplication.translate("Patcher", "All files")} (*.*)'
        )
        file_dialog.setDefaultSuffix("exe")
        if file_dialog.exec():
            self.edit_save_path.setText(file_dialog.selectedFiles()[0])

    def patch_game(self):
        self.button_patch.setEnabled(False)
        if not self.edit_executable_path.text():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title=QCoreApplication.translate("Patcher", "No file selected"),
                content=QCoreApplication.translate(
                    "Patcher", "No Balatro.exe selected."
                ),
                target=self.edit_executable_path,
                parent=self,
                isClosable=True,
            )
            return
        if not self.edit_save_path.text():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title=QCoreApplication.translate("Patcher", "No file selected"),
                content=QCoreApplication.translate("Patcher", "No save file selected."),
                target=self.edit_save_path,
                parent=self,
                isClosable=True,
            )
            return

        executable_path = Path(self.edit_executable_path.text())
        output_path = Path(self.edit_save_path.text())
        selected_patchers = [i.text() for i in self.checkbox_patchers if i.isChecked()]
        output_type = self.config.get(self.config.outputType)

        if not executable_path.exists():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title=QCoreApplication.translate("Patcher", "File not found"),
                content=QCoreApplication.translate(
                    "Patcher", "Selected Balatro.exe not found."
                ),
                target=self.edit_executable_path,
                parent=self,
                isClosable=True,
            )
            return

        patchers.patch_executable(
            executable_path, output_path, selected_patchers, output_type
        )

        self.button_patch.setEnabled(True)
        TeachingTip.create(
            icon=InfoBarIcon.SUCCESS,
            title=QCoreApplication.translate("Patcher", "Success"),
            content=QCoreApplication.translate("Patcher", "Patching complete."),
            target=self.button_patch,
            parent=self,
            isClosable=True,
        )
