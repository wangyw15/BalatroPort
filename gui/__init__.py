import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QFileDialog,
    QMessageBox,
    QWidget,
)
from qfluentwidgets import (
    MSFluentWindow,
    PushButton,
    CheckBox,
    LineEdit,
    StrongBodyLabel,
    FluentIcon,
    InfoBarIcon,
    TeachingTip,
    OptionsSettingCard,
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
)

import patchers
from libs import love2d_helper


class Config(QConfig):
    outputType = OptionsConfigItem(
        "Patcher",
        "OutputType",
        love2d_helper.VALID_OUTPUT_TYPES[0],
        OptionsValidator(love2d_helper.VALID_OUTPUT_TYPES),
        restart=True,
    )


class PatcherWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("Patcher")
        self.config = Config()

        # widgets
        self.layout = QGridLayout(self)
        self.edit_executable_path = LineEdit(self)
        self.button_browse_executable = PushButton("Browse", self)
        self.edit_save_path = LineEdit(self)
        self.button_browse_save = PushButton("Browse", self)
        self.options_card_output_type = OptionsSettingCard(
            icon=FluentIcon.SAVE,
            configItem=self.config.outputType,
            title="Output type",
            content="Select the type of output file you want to generate.",
            texts=love2d_helper.VALID_OUTPUT_TYPES,
        )
        self.button_patch = PushButton("Patch", self)
        self.checkbox_patchers = []

        # layout
        for i, patcher_name in enumerate(patchers.get_patcher_names()):
            self.checkbox_patchers.append(CheckBox(patcher_name, self))
            self.layout.addWidget(self.checkbox_patchers[i], 1, i)

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
            StrongBodyLabel("Path to save", self), 4, 0, 1, self.layout.columnCount()
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
        output_type = self.config.get(self.config.outputType)

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


class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Balatro helper")
        self.addSubInterface(PatcherWidget(self), FluentIcon.APPLICATION, "Patcher")


def run():
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
