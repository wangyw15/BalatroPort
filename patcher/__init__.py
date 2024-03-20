from importlib import import_module
from pkgutil import iter_modules
from pathlib import Path


def get_patchers() -> dict[str, callable([[str], str])]:
    """
    Get all patch functions from the patcher module.
    "__" is interpreted as /
    "_" is interpreted as .
    :return: dict with patcher target file as key and patch function as value
    """
    for _, module_name, _ in iter_modules([str(Path(__file__).parent)]):
        if module_name.startswith("patcher_"):
            current_patcher = import_module(f"{Path(__file__).parent.name}.{module_name}")
            for member_name, member in current_patcher.__dict__.items():
                if member_name.startswith("patch_") and callable(member):
                    yield [member_name[6:].replace("__", "/").replace("_", "."), member]


def patch_file(file_path: Path | str, patch_function: callable([[str], str])) -> None:
    """
    Patch a file using a patch function.
    :param file_path: file to patch
    :param patch_function: patch function
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with file_path.open("r") as f:
        code = f.read()
    patched_code = patch_function(code)
    with file_path.open("w") as f:
        f.write(patched_code)


def patch_game(extracted_dir: Path | str) -> None:
    """
    Patch the game to run independently.
    :param extracted_dir: directory to patch
    """
    if isinstance(extracted_dir, str):
        extracted_dir = Path(extracted_dir)

    patchers = get_patchers()
    for patcher_target, patcher in patchers:
        patch_file(extracted_dir / patcher_target, patcher)


__all__ = [
    "patch_game"
]
