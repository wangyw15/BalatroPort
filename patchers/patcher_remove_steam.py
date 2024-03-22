import re


def patch_main__lua(code: str) -> str:
    """
    Remove the steam API from the code.
    :param code: code to remove the steam API from
    :return: code without steam API
    """
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    function_love_load = False

    for line in original_code_lines:
        if re.fullmatch(r"\s*function\s+love\.load\(\s*\)\s*", line):
            function_love_load = True

        if (function_love_load and
                re.fullmatch(r"\s*if\s+os\s+==\s+'OS X'\s+or\s+os\s+==\s+'Windows'\s+then\s*", line)):
            patched_code_lines.append("--" + line)
            patched_code_lines.append(re.compile(r"os\s+==\s+'OS X'\s+or\s+os\s+==\s+'Windows'")
                                        .sub("false", line))
            function_love_load = False
            continue
        patched_code_lines.append(line)

    return "\n".join(patched_code_lines)
