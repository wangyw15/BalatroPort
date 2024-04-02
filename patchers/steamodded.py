import re

from libs import steamodded_helper


def patch_main__lua(code: str) -> str:
    return code + "\n" + steamodded_helper.get_code()


def patch_game__lua(code: str) -> str:
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        patched_code_lines.append(line)
        if re.fullmatch(r"\s*self\.SPEEDFACTOR\s+=\s+1\s*", line):
            patched_code_lines.append("    initSteamodded()")

    return "\n".join(patched_code_lines)
