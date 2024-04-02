from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests

import util


def download_steamodded(version: str | None = None) -> bytes:
    """
    Download the Steamodded repository.
    :param version: version to download (default: latest)
    :return: downloaded content
    """
    if not version:
        version = util.get_latest_release_version("Steamopollys/Steamodded")

    url = f"https://github.com/Steamopollys/Steamodded/archive/refs/tags/{version}.zip"

    print(f"Downloading Steamodded v{version}...")
    with requests.get(url) as response:
        response.raise_for_status()
        return response.content


def get_code() -> str:
    directories = ["core", "debug", "loader"]
    core_file_name = "core.lua"
    code = ""

    with BytesIO(download_steamodded()) as steamodded_data:
        with ZipFile(steamodded_data) as steamodded_zip:
            for filename in steamodded_zip.namelist():
                filepath = Path(filename)
                if filepath.parent.name in directories:
                    with steamodded_zip.open(filename) as file:
                        if filepath.name == core_file_name:
                            code = file.read().decode() + "\n" + code
                        else:
                            code += file.read().decode() + "\n"
    return code
