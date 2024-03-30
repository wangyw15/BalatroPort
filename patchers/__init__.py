import shutil
from importlib import import_module
from io import BytesIO
from os import PathLike
from pathlib import Path
from pkgutil import iter_modules
from types import ModuleType

from libs import util, love2d_helper


def get_patcher_names() -> list[str]:
    """
    Get patcher names.
    :return: list of patcher names
    """
    ret: list[str] = []
    for _, module_name, _ in iter_modules([str(Path(__file__).parent)]):
        if module_name.startswith("patcher_"):
            ret.append(module_name[8:])
    return ret


def get_patchers() -> dict[str, ModuleType]:
    """
    Get patchers.
    :return: dict with patcher name as key and patcher module as value
    """
    ret: dict[str, ModuleType] = {}
    for _, module_name, _ in iter_modules([str(Path(__file__).parent)]):
        if module_name.startswith("patcher_"):
            current_patcher = import_module(
                f"{Path(__file__).parent.name}.{module_name}"
            )
            ret[module_name[8:]] = current_patcher
    return ret


def get_patches(
    patcher: ModuleType,
) -> dict[str, callable([[str, PathLike[str]], str])]:
    """
    Get all patch functions from the patcher module.
    "___" is interpreted as /
    "__" is interpreted as .
    :param patcher: patcher module
    :return: dict with patcher target file as key and patch function as value
    """
    ret: dict[str, callable([[str, PathLike[str]], str])] = {}
    for member_name, member in patcher.__dict__.items():
        if member_name.startswith("patch_") and callable(member):
            ret[member_name[6:].replace("___", "/").replace("__", ".")] = member
    return ret


def patch_file(
    file_path: Path | str,
    patch_function: callable([[str, PathLike[str]], str]),
    working_dir: Path | str,
) -> None:
    """
    Patch a file using a patch function.
    :param file_path: file to patch
    :param patch_function: patch function
    :param working_dir: working directory
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8") as f:
        code = f.read()
    patched_code = patch_function(code, working_dir)
    with file_path.open("w", encoding="utf-8") as f:
        f.write(patched_code)


def patch_extracted_game(working_dir: Path | str, patcher_name: str) -> None:
    """
    Patch the game to run independently.
    :param patcher_name: patcher to use
    :param working_dir: directory to patch
    """
    if isinstance(working_dir, str):
        working_dir = Path(working_dir)

    patchers = get_patchers()
    if patcher_name not in patchers:
        raise ValueError(f"Unknown patcher: {patcher_name}")
    patches = get_patches(patchers[patcher_name])
    for patcher_target, patcher in patches.items():
        patch_file(working_dir / "game" / patcher_target, patcher, working_dir)


def patch_game_data(
    game_data: bytes, selected_patchers: list[str] | None = None
) -> bytes:
    """
    Patch the game to run independently.
    :param game_data: game data
    :param selected_patchers: patchers to use
    """
    if selected_patchers is None:
        selected_patchers = []

    working_dir = Path(f"balatro_{util.random_string()}")
    working_dir.mkdir(exist_ok=False)
    uncompressed_game_dir = working_dir / "game"
    uncompressed_game_dir.mkdir(exist_ok=False)

    with BytesIO(game_data) as love_data_io:
        print("Extracting game data...")
        util.uncompress(love_data_io, uncompressed_game_dir)

    for patcher_name in selected_patchers:
        print(f"Patching with {patcher_name}...")
        patch_extracted_game(working_dir, patcher_name)

    with BytesIO() as love_data_io:
        print("Repacking game data...")
        util.compress(uncompressed_game_dir, love_data_io)
        patched_game_data = love_data_io.getvalue()

    shutil.rmtree(working_dir)
    return patched_game_data


def patch_executable(
    executable_path: Path | str,
    output_path: Path | str,
    selected_patchers: list[str] | None = None,
    output_type: str = "exe",
) -> None:
    """
    Patch the game to run independently.
    :param executable_path: executable path
    :param output_path: output path
    :param selected_patchers: patchers to use
    :param output_type: output type
    """
    if selected_patchers is None:
        selected_patchers = []

    if isinstance(executable_path, str):
        executable_path = Path(executable_path)
    if isinstance(output_path, str):
        output_path = Path(output_path)

    if not executable_path.exists():
        raise FileNotFoundError("Executable not found.")
    if output_type not in love2d_helper.VALID_OUTPUT_TYPES:
        raise ValueError(
            f'Invalid output type "{output_type}".\n'
            f'Available output types: "{", ".join(love2d_helper.VALID_OUTPUT_TYPES)}'
        )

    love_data = love2d_helper.get_game_data(executable_path)

    # apply patchers
    if selected_patchers:
        love_data = patch_game_data(love_data, selected_patchers)

    if output_type == "exe":
        executable_data = love2d_helper.get_game_executable(executable_path)
        with output_path.open("wb") as output_file:
            output_file.write(executable_data + love_data)
    elif output_type in ["love", "zip"]:
        with output_path.open("wb") as output_file:
            output_file.write(love_data)


__all__ = ["patch_executable", "patch_game_data", "get_patcher_names"]
