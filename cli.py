import argparse
import shutil
from io import BytesIO
from pathlib import Path

import libs.util
import patchers
from libs import love2d_helper, util, game_save_helper

VALID_OUTPUT_TYPES = ["exe", "love", "zip"]

parser = argparse.ArgumentParser(description="Balatro Helper")

subparsers = parser.add_subparsers(title="Subcommands", description="Available subcommands", dest="subcommand")

patcher_parser = subparsers.add_parser("patcher", help="Patcher")
patcher_parser.add_argument("-p", "--patcher",
                            type=str,
                            help="Patcher to use, available patchers: " + ", ".join(patchers.get_patcher_names()),
                            required=False,
                            nargs="+")
patcher_parser.add_argument("input", help="Path to Balatro.exe", type=str)
patcher_parser.add_argument("output", help="Output path", type=str)

game_save_parser = subparsers.add_parser("game-save", help="Game save helper")
game_save_parser.add_argument("-d", "--dump", help="Dump the save file", action="store_true")
game_save_parser.add_argument("-p", "--pack", help="Pack the save file", action="store_true")
game_save_parser.add_argument("input", help="Path to the save file", type=str)
game_save_parser.add_argument("output", help="Path to the output file", type=str)

args = parser.parse_args()


def patcher():
    executable_path = Path(args.input)
    selected_patchers: list[str] = args.patcher or []
    output_path = Path(args.output)
    output_type = output_path.suffix[1:].lower()

    if not executable_path.exists():
        raise FileNotFoundError("Executable not found.")
    if output_type not in VALID_OUTPUT_TYPES:
        raise ValueError(f'Invalid output type "{output_type}".\n'
                         f'Available output types: "{", ".join(VALID_OUTPUT_TYPES)}')

    love_data = love2d_helper.get_game_data(executable_path)

    # apply patchers
    if selected_patchers:
        for patcher_name in selected_patchers:
            if patcher_name not in patchers.get_patcher_names():
                raise ValueError(f'Patcher "{patcher_name}" not found.\n'
                                 f'Available patchers: {", ".join(patchers.get_patcher_names())}')

        working_dir = Path(f"balatro_{util.random_string()}")
        working_dir.mkdir(exist_ok=False)
        uncompressed_game_dir = working_dir / "game"
        uncompressed_game_dir.mkdir(exist_ok=False)

        with BytesIO(love_data) as love_data_io:
            print("Extracting game data...")
            libs.util.uncompress(love_data_io, uncompressed_game_dir)

        for patcher_name in selected_patchers:
            print(f"Patching with {patcher_name}...")
            patchers.patch_game(working_dir, patcher_name)

        with BytesIO() as love_data_io:
            print("Repacking game data...")
            libs.util.compress(uncompressed_game_dir, love_data_io)
            love_data = love_data_io.getvalue()

        shutil.rmtree(working_dir)

    if output_type == "exe":
        executable_data = love2d_helper.get_game_executable(executable_path)
        with output_path.open("wb") as output_file:
            output_file.write(executable_data + love_data)
    elif output_type in ["love", "zip"]:
        with output_path.open("wb") as output_file:
            output_file.write(love_data)


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


if __name__ == "__main__":
    if args.subcommand == "patcher":
        patcher()
    elif args.subcommand == "game-save":
        game_save()
    else:
        parser.print_help()
