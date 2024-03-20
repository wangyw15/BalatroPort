import re
from pathlib import Path


def remove_steam(code: str) -> str:
    """
    Remove the steam API from the code.
    :param code: code to remove the steam API from
    :return: code without steam API
    """
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    function_love_load = 0
    steam_integration = False
    function_love_quit = 0

    code_level = 0

    for line in original_code_lines:
        # calculate code level
        if not line.strip().startswith("--"):
            if re.fullmatch(r"\s*(function|if).*", line):
                code_level += 1
            elif re.fullmatch(r"\s*end\s*", line):
                code_level -= 1

        remove_line = False

        if re.fullmatch(r"\s*function\s+love\.load\(\s*\)\s*", line):
            function_love_load = code_level
        if re.fullmatch(r"\s*function\s+love\.quit\(\s*\)\s*", line):
            function_love_quit = code_level

        if function_love_load:
            if re.fullmatch(r"\s*--Steam\sintegration\s*", line):
                steam_integration = True
            remove_line = steam_integration
            if re.fullmatch(r"\s*end\s*", line) and code_level == function_love_load:
                steam_integration = False
                function_love_load = 0

        if function_love_quit:
            if re.fullmatch(r"\s*if\s*G\.STEAM\s*then\s*G\.STEAM:shutdown\(\s*\)\s*end\s*", line):
                remove_line = True
                function_love_quit = 0

        patched_code_lines.append(("--" if remove_line else "") + line)

    return "\n".join(patched_code_lines)


def patch_game(extracted_dir: Path | str) -> None:
    """
    Patch the game to run independently.
    :param extracted_dir: directory to patch
    """
    if isinstance(extracted_dir, str):
        extracted_dir = Path(extracted_dir)

    with open(extracted_dir / "main.lua", "r") as main_file:
        code = main_file.read()
    patched_code = remove_steam(code)
    with open(extracted_dir / "main.lua", "w") as main_file:
        main_file.write(patched_code)


__all__ = [
    "patch_game"
]
