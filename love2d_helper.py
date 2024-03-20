import zipfile
from pathlib import Path
from typing import BinaryIO

PK_SIGNATURE = b'PK\x05\x06'


def read_uint32(file_io: BinaryIO) -> int:
    """
    Read a 32-bit unsigned integer from the file.
    :param file_io: file to read from
    :return: 32-bit unsigned integer
    """
    data = file_io.read(4)
    number = data[0]
    number += data[1] << 8
    number += data[2] << 16
    number += data[3] << 24
    return number


def seek_zip(file_io: BinaryIO) -> None:
    """
    Seek to the beginning of the zip file inside the executable.
    :param file_io: file to read from
    """
    # retrieve the file size
    file_io.seek(0, 2)
    filesize = file_io.tell()

    # scan the last 65k (2^16) for the zip signature
    signature_position = filesize
    while signature_position > filesize - (2 << 16):
        file_io.seek(signature_position, 0)
        data = file_io.read(len(PK_SIGNATURE))
        if data == PK_SIGNATURE:
            break
        signature_position -= 1
    else:
        raise ValueError("Corrupted zip archive.")

    # skip 8 bytes
    file_io.seek(8, 1)

    # read size and offset of central directory
    size = read_uint32(file_io)
    offset = read_uint32(file_io)

    # Calculate beginning of the zip file:
    # There is a "central directory" with the size 'size' located at 'offset' (relative to the zip
    # file). The signature is appended directly after the central directory. We have already found
    # the signature start and know the size of the central directory, so we can calculate the
    # beginning of the central directory via 'signature_position - size'. The result is the "real"
    # offset inside the packed executable. The supposed offset inside the zip file is stored at
    # 'offset', so we can calculate the beginning of the zip-file.
    start = (signature_position - size) - offset

    # seek to the beginning position
    file_io.seek(start, 0)


def get_game_data(executable: Path | str) -> bytes:
    """
    Read the love data from the executable.
    :param executable: path to the executable
    :return: love data
    """
    if isinstance(executable, str):
        executable = Path(executable)

    with executable.open("rb") as executable:
        seek_zip(executable)
        return executable.read()


def unpack(love_file: Path | str, extract_dir: Path | str | None = None) -> None:
    """
    Extract the contents of a .love file to a directory.
    :param love_file: path to the .love file
    :param extract_dir: directory to extract to
    """
    if isinstance(love_file, str):
        love_file = Path(love_file)

    if extract_dir is None:
        extract_dir = love_file.parent / "game"
    elif isinstance(extract_dir, str):
        extract_dir = Path(extract_dir)

    if not zipfile.is_zipfile(love_file):
        raise ValueError("Not a valid zip file.")

    with zipfile.ZipFile(love_file, "r") as zip_file:
        zip_file.extractall(extract_dir)


def repack(extracted_dir: Path | str, love_file: Path | str | None = None) -> None:
    """
    Repack the contents of a directory to a .love file.
    :param extracted_dir: directory to pack
    :param love_file: path to the .love file
    """
    if isinstance(extracted_dir, str):
        extracted_dir = Path(extracted_dir)

    if love_file is None:
        love_file = extracted_dir.parent / "game.love"
    elif isinstance(love_file, str):
        love_file = Path(love_file)

    with zipfile.ZipFile(love_file, "w") as zip_file:
        for file in extracted_dir.rglob("*"):
            if file.is_file():
                zip_file.write(file, file.relative_to(extracted_dir))


__all__ = [
    "get_game_data"
]
