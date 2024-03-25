from pathlib import Path
from typing import BinaryIO

# https://github.com/love2d/love/blob/681d694f9df1b23d22b8bbb592e0913802da28c0/src/libraries/physfs/physfs_archiver_zip.c#L590
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


def get_game_data(executable_path: Path | str) -> bytes:
    """
    Read the love data from the executable.
    :param executable_path: path to the executable
    :return: love data
    """
    if isinstance(executable_path, str):
        executable_path = Path(executable_path)

    with executable_path.open("rb") as executable_file:
        seek_zip(executable_file)
        return executable_file.read()


def get_game_executable(executable_path: Path | str) -> bytes:
    """
    Read the executable without game data from the executable.
    :param executable_path: path to the executable
    :return: love executable
    """
    if isinstance(executable_path, str):
        executable_path = Path(executable_path)

    with executable_path.open("rb") as executable_file:
        seek_zip(executable_file)
        executable_length = executable_file.tell() - 1
        executable_file.seek(0, 0)
        return executable_file.read(executable_length)


__all__ = [
    "get_game_data",
]
