import argparse
import shutil
from io import BytesIO
from pathlib import Path

import patchers
from libs import love2d_helper, util

parser = argparse.ArgumentParser(description="Balatro Patcher")

parser.add_argument("-i", "--input",
                    type=str,
                    help="Path to Balatro.exe",
                    required=True)
parser.add_argument("-p", "--patcher",
                    type=str,
                    help="Patcher to use, available patchers: " + ", ".join(patchers.get_patcher_names()),
                    required=False,
                    nargs="+")
parser.add_argument("-o", "--output",
                    type=str,
                    help="Output path",
                    required=True)

args = parser.parse_args()

if __name__ == "__main__":
    executable_path = Path(args.input)
    selected_patchers: list[str] = args.patcher or []
    output_path = Path(args.output)

    love_data = love2d_helper.get_game_data(executable_path)

    # apply patchers
    if selected_patchers:
        temp_dir = Path(util.random_string())
        temp_dir.mkdir(exist_ok=False)

        with BytesIO(love_data) as love_data_io:
            print("Extracting game data...")
            love2d_helper.unpack(love_data_io, temp_dir)

        for patcher_name in selected_patchers:
            print(f"Patching with {patcher_name}...")
            patchers.patch_game(temp_dir, patcher_name)

        with BytesIO() as love_data_io:
            print("Repacking game data...")
            love2d_helper.repack(temp_dir, love_data_io)
            love_data = love_data_io.getvalue()

        shutil.rmtree(temp_dir)

    with output_path.open("wb") as output_file:
        output_file.write(love_data)
