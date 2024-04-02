import argparse
import subprocess
from os import PathLike
from pathlib import Path


def get_java_executable() -> str:
    return str((Path(__file__).parent.parent / "assets" / "jre" / "bin" / "java.exe").absolute())


def build_jre(jars: list[PathLike[str]], output: PathLike[str]) -> None:
    libs: set[str] = set()

    # get libs
    for jar in jars:
        result = subprocess.run(["jdeps", "--list-deps", jar], capture_output=True)
        for lib in result.stdout.decode().split("\n"):
            if lib.strip():
                libs.add(lib.strip().split("/")[0])

    # generate jre
    subprocess.run(
        [
            "jlink",
            "--no-header-files",
            "--no-man-pages",
            "--add-modules",
            ",".join(libs),
            "--output",
            output,
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JRE builder")
    parser.add_argument("output", help="Output path", type=str)
    parser.add_argument("-j", "--jars", help="Jar files", type=str, nargs="+")
    args = parser.parse_args()

    build_jre(args.jars, args.output)
