import re
from os import PathLike


def patch_conf__lua(code: str, working_dir: str | PathLike[str]) -> str:
    return re.compile(r"_RELEASE_MODE\s*=\s*true").sub("_RELEASE_MODE = false", code)
