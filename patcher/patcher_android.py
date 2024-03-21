import re


def patch_globals_lua(code: str) -> str:
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        if re.fullmatch(r"\s*loadstring\(\S*\)\(\)\s*", line):
            # enable the game to run on mobile
            patched_code_lines.append("--" + line)
            # mobile settings
            patched_code_lines.append("\n".join(""""
    if love.system.getOS() == 'Android' or love.system.getOS() == 'iOS' then
        self.F_DISCORD = false
        self.F_SAVE_TIMER = 5
        self.F_ENGLISH_ONLY = false
        self.F_CRASH_REPORTS = false
        self.F_SKIP_TUTORIAL = true
        self.F_VIDEO_SETTINGS = false
        self.F_QUIT_BUTTON = false
    end

            """.split("\n")[1:-1]))
        else:
            patched_code_lines.append(line)

    return "\n".join(patched_code_lines)


def patch_conf_lua(code: str) -> str:
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        patched_code_lines.append(line)
        if re.fullmatch(r"\s*function\s+love\.conf\s*\(\s*t\s*\)\s*", line):
            # save in /sdcard/Android/data
            patched_code_lines.append("\tt.externalstorage = true")

    return "\n".join(patched_code_lines)
