# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --standalone
# nuitka-project: --onefile
# nuitka-project: --output-dir=build
# nuitka-project: --company-name=wangyw15
# nuitka-project: --file-version=1.1.0
# nuitka-project: --product-version=1.1.0
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/icon.ico=icon.ico
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/i18n/*.qm=i18n/
# nuitka-project-if: {OS} == "Windows":
#     nuitka-project: --windows-icon-from-ico=icon.ico
# nuitka-project-if: __import__("libs.feature").feature.apk_packer_enabled():
#     nuitka-project: --product-name=BalatroHelperFull
#     nuitka-project: --output-filename=BalatroHelperFull.exe
#     nuitka-project: --include-data-dir={MAIN_DIRECTORY}/apk_packer_assets=apk_packer_assets
# nuitka-project-else:
#     nuitka-project: --product-name=BalatroHelper
#     nuitka-project: --output-filename=BalatroHelper.exe

import argparse
from pathlib import Path

import apk_packer
import patchers
from libs import love2d_helper, game_save_helper, feature

parser = argparse.ArgumentParser(description="Balatro Helper")

subparsers = parser.add_subparsers(
    title="Subcommands", description="Available subcommands", dest="subcommand"
)

patcher_parser = subparsers.add_parser("patcher", help="Patcher")
patcher_parser.add_argument("input", help="Path to Balatro.exe", type=str)
patcher_parser.add_argument("output", help="Output path", type=str)
patcher_parser.add_argument(
    "-p",
    "--patcher",
    type=str,
    help="Patcher to use, available patchers: "
    + ", ".join(patchers.get_patcher_names()),
    required=False,
    nargs="+",
)

game_save_parser = subparsers.add_parser("game-save", help="Game save helper")
game_save_parser.add_argument(
    "-d", "--dump", help="Dump the save file", action="store_true"
)
game_save_parser.add_argument(
    "-p", "--pack", help="Pack the save file", action="store_true"
)
game_save_parser.add_argument("input", help="Path to the save file", type=str)
game_save_parser.add_argument("output", help="Path to the output file", type=str)

pack_apk_parser = subparsers.add_parser("pack-apk", help="Pack APK")
pack_apk_parser.add_argument("input", help="Path to the game.love", type=str)
pack_apk_parser.add_argument("output", help="Path to the output APK", type=str)

args = parser.parse_args()


def patcher():
    executable_path = Path(args.input)
    selected_patchers: list[str] = args.patcher or []
    output_path = Path(args.output)
    output_type = output_path.suffix[1:].lower()

    if not executable_path.exists():
        raise FileNotFoundError("Executable not found.")
    if output_type not in love2d_helper.VALID_OUTPUT_TYPES:
        raise ValueError(
            f'Invalid output type "{output_type}".\n'
            f'Available output types: "{", ".join(love2d_helper.VALID_OUTPUT_TYPES)}'
        )

    # apply patchers
    patchers.patch_executable(
        executable_path, output_path, selected_patchers, output_type
    )


def game_save():
    if args.dump and args.pack:
        raise ValueError("Cannot dump and pack at the same time")

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f'"{input_path}" not found')

    if args.dump:
        with input_path.open("rb") as fi:
            with output_path.open("w") as fo:
                data = fi.read()
                uncompressed = game_save_helper.inflate(data)
                fo.write(uncompressed)

    if args.pack:
        with input_path.open("r") as fi:
            with output_path.open("wb") as fo:
                data = fi.read()
                compressed = game_save_helper.deflate(data)
                fo.write(compressed)


def pack_apk():
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f'"{input_path}" not found')

    game_content = input_path.read_bytes()
    apk_packer.pack_game_apk(game_content, output_path)
    print("APK packed successfully.")


def main():
    if feature.apk_packer_enabled():
        print("Full version")
    if args.subcommand == "patcher":
        patcher()
    elif args.subcommand == "game-save":
        game_save()
    elif args.subcommand == "pack-apk":
        pack_apk()
    else:
        import gui

        print("Loading GUI...")
        gui.run()


if __name__ == "__main__":
    main()
