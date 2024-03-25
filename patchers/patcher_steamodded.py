# https://github.com/Steamopollys/Steamodded/blob/main/steamodded_injector.py
import re
from os import PathLike
from pathlib import Path

import requests

from libs import util


def download_steamodded(download_path: str | PathLike[str]) -> None:
    """
    Download the Steamodded repository.
    :param download_path: path to download the repository to
    """
    url = "https://github.com/Steamopollys/Steamodded/archive/refs/heads/main.zip"

    if isinstance(download_path, str):
        download_path = Path(download_path)

    print("Downloading Steamodded...")
    with requests.get(url) as response:
        response.raise_for_status()

        with download_path.open("wb") as file:
            file.write(response.content)


def read_code_from_directory(directory: str | PathLike[str]) -> str:
    """
    Read the all the lua code from the directory.
    :param directory: directory to read the code from
    :return: combined code
    """
    if isinstance(directory, str):
        directory = Path(directory)

    code = ""
    for src_files in directory.glob("*.lua"):
        with src_files.open() as src_file:
            code += src_file.read() + "\n"
    return code


def patch_main__lua(code: str, working_dir: str | PathLike[str]) -> str:
    if isinstance(working_dir, str):
        working_dir = Path(working_dir)

    directories = ["core", "debug", "loader"]

    steamodded_file = working_dir / "steamodded.zip"
    steamodded_dir = working_dir / "Steamodded-main"

    if not steamodded_dir.exists():
        if not steamodded_file.exists():
            download_steamodded(steamodded_file)
        util.uncompress(steamodded_file, working_dir)

    result = code
    for directory in directories:
        result += '\n' + read_code_from_directory(steamodded_dir / directory)

    return result


def patch_game__lua(code: str, working_dir: str | PathLike[str]) -> str:
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        patched_code_lines.append(line)
        if re.fullmatch(r"\s*self\.SPEEDFACTOR\s+=\s+1\s*", line):
            patched_code_lines.append("    initSteamodded()")

    return "\n".join(patched_code_lines)
