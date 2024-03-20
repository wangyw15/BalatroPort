import re


def patch_main_lua(code: str) -> str:
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


def patch_globals_lua(code: str) -> str:
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        if re.fullmatch(r"\s*loadstring\(\S*\)\(\)\s*", line):
            patched_code_lines.append("--" + line)
            patched_code_lines.append("\n".join(""""
    if love.system.getOS() == 'Android' then
        self.F_DISCORD = false
        self.F_SAVE_TIMER = 5
        self.F_ENGLISH_ONLY = false
        self.F_CRASH_REPORTS = false
        self.F_SKIP_TUTORIAL = false
    end

            """.split("\n")[1:-1]))
        else:
            patched_code_lines.append(line)

    return "\n".join(patched_code_lines)
