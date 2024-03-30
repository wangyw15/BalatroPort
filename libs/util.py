import zipfile
from datetime import datetime
from hashlib import md5
from os import PathLike
from pathlib import Path
from typing import IO


def random_string(length: int = 10) -> str:
    """
    Generate a random string.
    :param length: length of the string, max 32
    :return: random string
    """
    length = min(max(1, length), 32)
    return md5(str(datetime.now()).encode()).hexdigest()[:length]


def compress(
    directory: Path | str, zip_file: str | PathLike[str] | IO[bytes] | None = None
) -> None:
    """
    Compress the contents of a directory.
    :param directory: directory to compress
    :param zip_file: path to the zip file
    """
    if isinstance(directory, str):
        directory = Path(directory)

    if zip_file is None:
        zip_file = directory / "game.love"
    elif isinstance(zip_file, str):
        zip_file = Path(zip_file)

    with zipfile.ZipFile(zip_file, "w") as zip_file:
        for file in directory.rglob("*"):
            if file.is_file():
                zip_file.write(file, file.relative_to(directory))


def uncompress(
    zip_file: str | PathLike[str] | IO[bytes], directory: Path | str | None = None
) -> None:
    """
    Extract the contents of a zip file.
    :param zip_file: path to the zip file
    :param directory: directory to extract to
    """
    if isinstance(zip_file, str):
        zip_file = Path(zip_file)

    if directory is None:
        directory = zip_file.parent / "game"
    elif isinstance(directory, str):
        directory = Path(directory)

    if not zipfile.is_zipfile(zip_file):
        raise ValueError("Not a valid zip file.")

    with zipfile.ZipFile(zip_file, "r") as zip_file:
        zip_file.extractall(directory)


__all__ = [
    "random_string",
    "compress",
    "uncompress",
]
