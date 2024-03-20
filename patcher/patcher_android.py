import re


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
