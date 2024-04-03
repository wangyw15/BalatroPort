import os
from pathlib import Path


def apk_packer_enabled() -> bool:
    if result := os.getenv("BALATRO_HELPER_APK_PACKER"):
        if result.lower() == "false":
            return False
    if (Path(__file__).parent.parent / "apk_packer_assets").exists():
        return True
    return False
