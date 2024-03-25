import re
from os import PathLike


def patch_globals__lua(code: str, working_dir: str | PathLike[str]) -> str:
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


def patch_conf__lua(code: str, working_dir: str | PathLike[str]) -> str:
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        patched_code_lines.append(line)
        if re.fullmatch(r"\s*function\s+love\.conf\s*\(\s*t\s*\)\s*", line):
            # save in /sdcard/Android/data
            patched_code_lines.append("\tt.externalstorage = true")

    return "\n".join(patched_code_lines)


def patch_main__lua(code: str, working_dir: str | PathLike[str]) -> str:
    # force landscape mode
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        patched_code_lines.append(line)
        if re.fullmatch(r"\s*function\s+love\.load\(\s*\)\s*", line):
            patched_code_lines.append("""
	-- force landscape mode
	local width, height, flags = love.window.getMode()
	flags.resizable = false
	love.window.setMode(width, height, flags)
            """.lstrip("\n").rstrip(" "))

    patched_code_lines.append("""
-- force landscape mode
function love.displayrotated(index, orientation)
	local os = love.system.getOS()
	if os == "Android" or os == "iOS" then
		if orientation == "portrait" or "portraitflipped" then
		local width, height, flags = love.window.getMode()
			if index == flags.display then
				if height > width then
					-- just to make sure
					flags.resizable = false
					love.window.setMode(height, width, flags)
				end
			end
		end
	end
end
    """.lstrip("\n").rstrip(" "))

    return "\n".join(patched_code_lines)


def patch_functions___UI_definitions__lua(code: str, working_dir: str | PathLike[str]) -> str:
    # quit button still raise problems
    return code
    # add quit button to the option menu
    original_code_lines = code.split("\n")
    patched_code_lines: list[str] = []

    for line in original_code_lines:
        patched_code_lines.append(line)
        if re.search(r"UIBox_button.*b_stats", line):
            patched_code_lines.append("  local exit_button = UIBox_button{ label = {localize('b_quit_cap')}, button = 'quit', minw = 5}")
        elif re.fullmatch(r"\s*credits\s*", line):
            patched_code_lines[-1] += ','
            patched_code_lines.append("exit_button")

    return "\n".join(patched_code_lines)
