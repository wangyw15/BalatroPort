import ctypes
import platform

import PySimpleGUI as sg

import patchers
from pathlib import Path

from libs import love2d_helper


class Window:
    def __init__(self):
        self.layout = [
            [sg.Text("Select patchers")],
            [sg.Checkbox(x, key=f"patcher_{x}") for x in patchers.get_patcher_names()],
            [sg.Text("Select Balatro.exe")],
            [
                sg.InputText(key="executable_path", readonly=True, enable_events=True),
                sg.FileBrowse(
                    "Browse", file_types=(("Balatro.exe", ".exe"),), enable_events=True
                ),
            ],
            [sg.Text("Save type")],
            [
                sg.Radio(
                    x,
                    0,
                    key=f"save_type_{x}",
                    default=(x == love2d_helper.VALID_OUTPUT_TYPES[0]),
                )
                for x in love2d_helper.VALID_OUTPUT_TYPES
            ],
            [sg.Text("Path to save")],
            [
                sg.InputText(key="save_path", readonly=True, enable_events=True),
                sg.FileSaveAs(
                    "Save",
                    file_types=(
                        ("Executable file", ".exe"),
                        ("Zipped game", ".love .zip"),
                    ),
                    enable_events=True,
                ),
            ],
            [sg.Button("Patch"), sg.Exit()],
        ]

    def show(self):
        window = sg.Window("Balatro helper", self.layout)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                break
            elif event == "executable_path":
                executable_path = Path(values["executable_path"])

                save_type = love2d_helper.VALID_OUTPUT_TYPES[0]
                for k, v in values.items():
                    if k.startswith("save_type_") and v:
                        save_type = k[10:]
                        break

                window["save_path"].update(
                    executable_path.parent
                    / f"{executable_path.stem}_patched.{save_type}"
                )
            elif event == "save_path":
                window[f"save_type_{Path(values['save_path']).suffix[1:]}"].update(True)
            elif event == "Patch":
                executable_path = Path(values["executable_path"])
                selected_patchers: list[str] = []
                output_path = Path(values["save_path"])
                output_type = output_path.suffix[1:].lower()

                # get selected patchers and output type
                for k, v in values.items():
                    if k.startswith("patcher_") and v:
                        selected_patchers.append(k[8:])
                    if k.startswith("save_type_") and v:
                        output_type = k[10:]

                # check if the executable exists
                if not executable_path.exists():
                    sg.PopupError("Executable not found.", title="File not found")
                    continue
                if output_type not in love2d_helper.VALID_OUTPUT_TYPES:
                    sg.PopupError(
                        f'Invalid output type "{output_type}".\n'
                        f'Available output types: "{", ".join(love2d_helper.VALID_OUTPUT_TYPES)}',
                        title="Invalid type",
                    )
                    continue

                # apply patchers
                patchers.patch_executable(
                    executable_path, output_path, selected_patchers, output_type
                )

                sg.Popup("Patching complete", title="Success")

        window.close()


def run():
    # dpi aware
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    Window().show()
