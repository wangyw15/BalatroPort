from os import PathLike
from pathlib import Path

import requests
import re


def get_latest_release_version() -> str:
    """
    Get the latest release version of Steamodded.
    :return: latest release version
    """
    url = "https://github.com/Steamopollys/Steamodded/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    if result := re.search(r"tag/([0-9.]+)", response.url):
        return result.group(1)
    return ""


def download_steamodded(download_path: str | PathLike[str], version: str | None = None) -> None:
    """
    Download the Steamodded repository.
    :param download_path: path to download the repository to
    :param version: version to download (default: latest)
    """
    if not version:
        version = get_latest_release_version()

    url = f"https://github.com/Steamopollys/Steamodded/archive/refs/tags/{version}.zip"

    if isinstance(download_path, str):
        download_path = Path(download_path)

    print(f"Downloading Steamodded v{version}...")
    with requests.get(url) as response:
        response.raise_for_status()

        with download_path.open("wb") as file:
            file.write(response.content)
