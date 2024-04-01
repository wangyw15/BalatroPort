import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QFileDialog,
    QMessageBox,
    QFrame,
)
from qfluentwidgets import (
    FluentWindow,
    PushButton,
    RadioButton,
    CheckBox,
    LineEdit,
    StrongBodyLabel,
    FluentIcon,
    InfoBarIcon,
    TeachingTip,
)

import patchers
from libs import love2d_helper


class PatcherWidget(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Patcher")

        # widgets
        self.layout = QGridLayout(self)
        self.edit_executable_path = LineEdit(self)
        self.button_browse_executable = PushButton("Browse", self)
        self.edit_save_path = LineEdit(self)
        self.button_browse_save = PushButton("Browse", self)
        self.button_patch = PushButton("Patch", self)
        self.checkbox_patchers = []
        self.checkbox_output_types = []

        # layout
        for i, patcher_name in enumerate(patchers.get_patcher_names()):
            self.checkbox_patchers.append(CheckBox(patcher_name, self))
            self.layout.addWidget(self.checkbox_patchers[i], 1, i)
        for i, output_type in enumerate(love2d_helper.VALID_OUTPUT_TYPES):
            self.checkbox_output_types.append(RadioButton(output_type, self))
            self.layout.addWidget(self.checkbox_output_types[i], 5, i)
            if i == 0:
                self.checkbox_output_types[i].setChecked(True)

        self.layout.addWidget(
            StrongBodyLabel("Select patchers", self), 0, 0, 1, self.layout.columnCount()
        )
        self.layout.addWidget(
            StrongBodyLabel("Select Balatro.exe", self),
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
            StrongBodyLabel("Save type", self), 4, 0, 1, self.layout.columnCount()
        )
        self.layout.addWidget(
            StrongBodyLabel("Path to save", self), 6, 0, 1, self.layout.columnCount()
        )
        self.layout.addWidget(
            self.edit_save_path, 7, 0, 1, self.layout.columnCount() - 1
        )
        self.layout.addWidget(self.button_browse_save, 7, self.layout.columnCount() - 1)
        self.layout.addWidget(self.button_patch, 8, 0, 1, self.layout.columnCount())

        # signals
        self.button_browse_executable.clicked.connect(self.browse_executable)
        self.button_browse_save.clicked.connect(self.browse_save)
        self.button_patch.clicked.connect(self.patch_game)

    def browse_executable(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Balatro executable (*.exe)")
        if file_dialog.exec():
            self.edit_executable_path.setText(file_dialog.selectedFiles()[0])

    def browse_save(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setNameFilter(
            "Executable file (*.exe);;Game only (*.love);;All files (*.*)"
        )
        file_dialog.setDefaultSuffix("exe")
        if file_dialog.exec():
            self.edit_save_path.setText(file_dialog.selectedFiles()[0])

    def patch_game(self):
        if not self.edit_executable_path.text():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title="No file selected",
                content="No Balatro.exe selected.",
                target=self.edit_executable_path,
                parent=self,
                isClosable=True,
            )
            return
        if not self.edit_save_path.text():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title="No file selected",
                content="No save file selected.",
                target=self.edit_save_path,
                parent=self,
                isClosable=True,
            )
            return

        executable_path = Path(self.edit_executable_path.text())
        output_path = Path(self.edit_save_path.text())
        selected_patchers = [i.text() for i in self.checkbox_patchers if i.isChecked()]
        output_type = [i.text() for i in self.checkbox_output_types if i.isChecked()][0]

        if not executable_path.exists():
            TeachingTip.create(
                icon=InfoBarIcon.ERROR,
                title="File not found",
                content="Selected Balatro.exe not found.",
                target=self.button_patch,
                parent=self,
                isClosable=True,
            )
            return

        patchers.patch_executable(
            executable_path, output_path, selected_patchers, output_type
        )

        QMessageBox.information(self, "Success", "Patching complete.")


class Window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Balatro helper")
        self.addSubInterface(PatcherWidget(self), FluentIcon.APPLICATION, "Patcher")


def run():
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
