import subprocess
from os import PathLike

from . import assets, java


def unpack_apk(apk_path: PathLike[str], output_dir: PathLike[str]) -> None:
    subprocess.run(
        [
            java.get_java_executable(),
            "-jar",
            (assets.assets_directory / "apktool.jar").absolute(),
            "d",
            "-s",
            "-o",
            output_dir,
            apk_path,
        ]
    )


def pack_apk(apk_dir: PathLike[str], output_apk: PathLike[str]) -> None:
    subprocess.run(
        [
            java.get_java_executable(),
            "-jar",
            (assets.assets_directory / "apktool.jar").absolute(),
            "b",
            "-o",
            output_apk,
            apk_dir,
        ]
    )


def sign_apk(apk_path: PathLike[str]) -> None:
    subprocess.run(
        [
            java.get_java_executable(),
            "-jar",
            (assets.assets_directory / "uber-apk-signer.jar").absolute(),
            "--apks",
            apk_path,
        ]
    )
