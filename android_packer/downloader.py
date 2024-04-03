import re

import requests

from libs import util


def download_embed_apk(version: str | None = None) -> bytes:
    if not version:
        version = util.get_latest_release_version("love2d/love-android")
    download_version = re.compile(r"[^.0-9]").sub("", version)
    url = (
        f"https://github.com/love2d/love-android/releases/"
        f"download/{version}/love-{download_version}-android-embed.apk"
    )

    print(f"Downloading love2d-android v{version}...")
    with requests.get(url) as response:
        response.raise_for_status()
        return response.content


def download_apktool(version: str | None = None) -> bytes:
    if not version:
        version = util.get_latest_release_version("iBotPeaches/Apktool")
    url = f"https://github.com/iBotPeaches/Apktool/releases/download/v{version}/apktool_{version}.jar"

    print(f"Downloading Apktool v{version}...")
    with requests.get(url) as response:
        response.raise_for_status()
        return response.content


def download_apk_signer(version: str | None = None) -> bytes:
    if not version:
        version = util.get_latest_release_version("patrickfav/uber-apk-signer")
    url = f"https://github.com/patrickfav/uber-apk-signer/releases/download/v{version}/uber-apk-signer-{version}.jar"

    print(f"Downloading uber-apk-signer v{version}...")
    with requests.get(url) as response:
        response.raise_for_status()
        return response.content
