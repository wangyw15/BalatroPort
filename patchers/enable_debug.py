import re


def patch_conf__lua(code: str) -> str:
    return re.compile(r"_RELEASE_MODE\s*=\s*true").sub("_RELEASE_MODE = false", code)
