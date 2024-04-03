import shutil
from pathlib import Path

from libs import util
from . import apk_helper, assets, downloader, java


def pack_game_apk(game_content: bytes, save_apk_path: Path | str) -> bytes:
    if isinstance(save_apk_path, str):
        save_apk_path = Path(save_apk_path)

    # create working dir
    working_dir = Path(f"balatro_apk_{util.random_string()}")
    working_dir.mkdir(exist_ok=False)

    # unpack apk
    unpacked_dir = working_dir / "unpacked_apk"
    apk_helper.unpack_apk(assets.assets_directory / "love-embed.apk", unpacked_dir)

    # update AndroidManifest.xml
    with (assets.assets_directory / "AndroidManifest.xml").open("r") as manifest_file:
        manifest_content: str = manifest_file.read()
        manifest_content = manifest_content.replace("${GamePackageName}", "com.anyone.balatro")
        manifest_content = manifest_content.replace("${GameVersionCode}", "1")
        manifest_content = manifest_content.replace("${GameVersionSemantic}", "CUSTOM_BUILD")
        manifest_content = manifest_content.replace("${GameName}", "Balatro")
        manifest_content = manifest_content.replace("${ORIENTATION}", "sensorLandscape")
    with (unpacked_dir / "AndroidManifest.xml").open("w") as manifest_file:
        manifest_file.write(manifest_content)

    # copy game content
    with (unpacked_dir / "assets" / "game.love").open("wb") as game_file:
        game_file.write(game_content)

    # replace icons
    target_resolution = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
    for resolution in target_resolution:
        icon_path = unpacked_dir / "res" / f"drawable-{resolution}" / "love.png"
        with icon_path.open("wb") as icon_file:
            icon_file.write((assets.assets_directory / "icons" / f"{resolution}.png").read_bytes())

    # repack apk
    packed_apk = working_dir / "balatro_unsigned.apk"
    apk_helper.pack_apk(unpacked_dir, packed_apk)

    # sign apk
    apk_helper.sign_apk(packed_apk)

    # move apk
    if save_apk_path.exists():
        save_apk_path.unlink()
    (working_dir / f"{packed_apk.stem}-aligned-debugSigned.apk").rename(save_apk_path)

    # cleanup working dir
    shutil.rmtree(working_dir)
