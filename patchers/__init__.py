from importlib import import_module
from os import PathLike
from pathlib import Path
from pkgutil import iter_modules
from types import ModuleType


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
            current_patcher = import_module(f"{Path(__file__).parent.name}.{module_name}")
            ret[module_name[8:]] = current_patcher
    return ret


def get_patches(patcher: ModuleType) -> dict[str, callable([[str, PathLike[str]], str])]:
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


def patch_file(file_path: Path | str,
               patch_function: callable([[str, PathLike[str]], str]),
               working_dir: Path | str) -> None:
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


def patch_game(working_dir: Path | str, patcher_name: str) -> None:
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


__all__ = [
    "patch_game",
    "get_patcher_names"
]
