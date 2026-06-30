from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

RUNTIME_MODULES = [
    "annotated_types",
    "boto3",
    "botocore",
    "dateutil",
    "jmespath",
    "pydantic",
    "pydantic_core",
    "s3transfer",
    "six",
    "typing_extensions",
    "typing_inspection",
    "urllib3",
]


def copy_module(module_name: str, target_dir: Path) -> None:
    spec = importlib.util.find_spec(module_name)
    if spec is None or spec.origin is None:
        raise RuntimeError(f"module {module_name} is not installed")

    if spec.submodule_search_locations:
        source = Path(next(iter(spec.submodule_search_locations)))
        destination = target_dir / source.name
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        return

    source_file = Path(spec.origin)
    shutil.copy2(source_file, target_dir / source_file.name)


def zip_directory(source_dir: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(source_dir.rglob("*")):
            if "__pycache__" in file.parts or file.suffix == ".pyc":
                continue
            if file.is_file():
                archive.write(file, file.relative_to(source_dir))


def install_linux_runtime(project_dir: Path, target_dir: Path) -> None:
    pyproject = tomllib.loads((project_dir / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"]["dependencies"]
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--upgrade",
            "--target",
            str(target_dir),
            "--platform",
            "manylinux2014_x86_64",
            "--implementation",
            "cp",
            "--python-version",
            "3.12",
            "--abi",
            "cp312",
            "--only-binary=:all:",
            *dependencies,
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="backend/src/tariffguard")
    parser.add_argument("--target", default="/tmp/tariffguard-lambda-build")
    parser.add_argument("--output")
    parser.add_argument("--project", default="backend")
    parser.add_argument("--install-runtime", action="store_true")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    target = Path(args.target).resolve()

    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)

    shutil.copytree(source, target / "tariffguard")
    if args.install_runtime:
        install_linux_runtime(Path(args.project).resolve(), target)
    else:
        for module_name in RUNTIME_MODULES:
            copy_module(module_name, target)

    if args.output:
        zip_directory(target, Path(args.output).resolve())


if __name__ == "__main__":
    main()
