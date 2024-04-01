import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QGridLayout,
    QLabel,
    QFileDialog,
    QCheckBox,
    QLineEdit,
    QRadioButton,
    QMessageBox,
)

import patchers
from libs import love2d_helper


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Balatro helper")

        self.layout = QGridLayout(self)
        self.edit_executable_path = QLineEdit()
        self.button_browse_executable = QPushButton("Browse")
        self.edit_save_path = QLineEdit()
        self.button_browse_save = QPushButton("Browse")
        self.button_patch = QPushButton("Patch")
        self.checkbox_patchers = []
        self.checkbox_output_types = []

        for i, patcher_name in enumerate(patchers.get_patcher_names()):
            self.checkbox_patchers.append(QCheckBox(patcher_name))
            self.layout.addWidget(self.checkbox_patchers[i], 1, i)
        for i, output_type in enumerate(love2d_helper.VALID_OUTPUT_TYPES):
            self.checkbox_output_types.append(QRadioButton(output_type))
            self.layout.addWidget(self.checkbox_output_types[i], 5, i)
            if i == 0:
                self.checkbox_output_types[i].setChecked(True)

        self.layout.addWidget(
            QLabel("Select patchers"), 0, 0, 1, self.layout.columnCount()
        )
        self.layout.addWidget(
            QLabel("Select Balatro.exe"), 2, 0, 1, self.layout.columnCount()
        )
        self.layout.addWidget(
            self.edit_executable_path, 3, 0, 1, self.layout.columnCount() - 1
        )
        self.layout.addWidget(
            self.button_browse_executable, 3, self.layout.columnCount() - 1
        )
        self.layout.addWidget(QLabel("Save type"), 4, 0, 1, self.layout.columnCount())
        self.layout.addWidget(
            QLabel("Path to save"), 6, 0, 1, self.layout.columnCount()
        )
        self.layout.addWidget(
            self.edit_save_path, 7, 0, 1, self.layout.columnCount() - 1
        )
        self.layout.addWidget(self.button_browse_save, 7, self.layout.columnCount() - 1)
        self.layout.addWidget(self.button_patch, 8, 0, 1, self.layout.columnCount())

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
        if not self.edit_executable_path.text() or not self.edit_save_path.text():
            QMessageBox.critical(
                self, "Missing data", "Please select path."
            )
            return

        executable_path = Path(self.edit_executable_path.text())
        output_path = Path(self.edit_save_path.text())
        selected_patchers = [i.text() for i in self.checkbox_patchers if i.isChecked()]
        output_type = [i.text() for i in self.checkbox_output_types if i.isChecked()][0]

        if not executable_path.exists():
            QMessageBox.critical(
                self, "File not found", "Selected Balatro.exe not found."
            )
            return

        patchers.patch_executable(
            executable_path, output_path, selected_patchers, output_type
        )

        QMessageBox.information(self, "Success", "Patching complete.")


def run():
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
