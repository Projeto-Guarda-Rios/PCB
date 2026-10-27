#!/usr/bin/env python3

import argparse
import logging
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Sequence, TypeAlias

ENV = os.environ.copy()
PYTHON_EXECUTABLE = sys.executable
BASE_DIR = pathlib.Path(__file__).resolve().parent
KICADMODTREE_DIR = BASE_DIR / "KicadModTree"

# Type alias for subprocess command, which can be a string or a sequence of strings/paths.
Command: TypeAlias = str | Sequence[str | pathlib.Path]


class DependencyException(Exception):
    def __init__(self, dependencies: list[str]) -> None:
        self.dependencies = dependencies

    def __str__(self) -> str:
        return f"Could not locate dependencies: '{", ".join(self.dependencies)}'"


def run_command(cmd: Command, *, cwd: str | pathlib.Path | None = None) -> None:
    logging.info(f"Running command: {_format_command(cmd)}")
    subprocess.run(
        cmd,
        bufsize=1,
        universal_newlines=True,
        env=ENV,
        check=True,
        cwd=cwd,
    )


def _format_command(cmd: Command) -> str:
    """Format a subprocess command for display in error messages."""
    if isinstance(cmd, str):
        return cmd
    return " ".join(str(part) for part in cmd)


def check_dependency(dependency: str) -> bool:
    if shutil.which(dependency):
        print(f"{dependency} - OK")
        return True

    print(f"{dependency} - NOT FOUND")
    return False


def check_dependencies(dependencies: list[str]) -> None:
    print("Checking dependencies...")

    missing: list[str] = []

    for dependency in dependencies:
        if not check_dependency(dependency):
            missing.append(dependency)

    if missing:
        raise DependencyException(missing)


def format_check(args: argparse.Namespace) -> None:
    check_dependencies(["pycodestyle", "black", "isort"])

    print("Performing footprint formatting check...")
    # TODO: Implement pycodestyle pythonically

    run_command(
        [
            "pycodestyle",
            "--max-line-length=120",
            KICADMODTREE_DIR,
            BASE_DIR / "src/kilibs/geom",
        ]
    )

    clean_files = [
        BASE_DIR / "kilt_manage.py",
        KICADMODTREE_DIR / "nodes/specialized/RoundRectangle.py",
        KICADMODTREE_DIR / "nodes/specialized/Stadium.py",
        KICADMODTREE_DIR / "nodes/specialized/Trapezoid.py",
        BASE_DIR / "src/kilibs",
        BASE_DIR / "tests",
        BASE_DIR / "src/generators/tools/footprint/drawing_tools.py",
        BASE_DIR / "src/generators/tools/footprint/misc_tools.py",
        BASE_DIR / "src/generators/tools/footprint/nodes/layouts",
        BASE_DIR / "src/generators/generate.py",
        BASE_DIR / "src/generators/connector/D_sub",
        BASE_DIR / "src/generators/LED/SMD",
        BASE_DIR / "src/generators/terminal_block/Barrier",
    ]

    run_command(["black", "--check", *clean_files])
    run_command(["isort", "--check-only", *clean_files])


def flake8_check(args: argparse.Namespace) -> None:
    check_dependencies(["flake8"])

    print("Performing flake8 validation...")

    run_command(
        [
            "flake8",
            KICADMODTREE_DIR,
            BASE_DIR / "src/kilibs/geom",
        ]
    )


def run_shellcheck(args: argparse.Namespace) -> None:
    check_dependencies(["shellcheck"])

    print("Running shellcheck...")
    gitlabci = BASE_DIR / "library_utils/tools/gitlabci"
    scripts = gitlabci.glob("*.sh")
    run_command(["shellcheck", *scripts], cwd=gitlabci)


def unit_tests(args: argparse.Namespace) -> None:
    print("Running footprint unit tests...")
    run_command([PYTHON_EXECUTABLE, "-m", "pytest"])


def py_test_coverage(args: argparse.Namespace) -> None:
    print("Checking unit test coverage...")
    ENV["PYTHONPATH"] = str(BASE_DIR)
    run_command(
        [
            PYTHON_EXECUTABLE,
            "-m",
            "nose2",
            "-C",
            "--coverage",
            KICADMODTREE_DIR,
            "--coverage-report",
            "term-missing",
            "-s",
            KICADMODTREE_DIR / "tests",
        ]
    )


def tests(args: argparse.Namespace) -> None:
    unit_tests(args)
    format_check(args)
    static_type_check(args)


def _do_pip_e_install(extras: str | list[str] | None = None) -> None:
    cmd = [PYTHON_EXECUTABLE, "-m", "pip", "install", "--upgrade", "-e"]

    target = "."
    if extras:
        if isinstance(extras, list):
            extras = ",".join(extras)
        target += f"[{extras}]"

    cmd.append(target)
    run_command(cmd)


def update_packages(args: argparse.Namespace) -> None:
    print("Updating packages required for production...")
    _do_pip_e_install()


def update_dev_packages(args: argparse.Namespace) -> None:
    print("Updating packages required for development...")
    _do_pip_e_install("dev")


def update_3d_packages(args: argparse.Namespace) -> None:
    print("Updating packages required for generating 3D models...")
    _do_pip_e_install("3d")


def update_doc_packages(args: argparse.Namespace) -> None:
    print("Updating packages required for generating documentation...")
    _do_pip_e_install("documentation")


def update_all_packages(args: argparse.Namespace) -> None:
    print("Updating all packages...")
    _do_pip_e_install(["3d", "dev", "documentation"])


def static_type_check(args: argparse.Namespace) -> None:
    check_dependencies(["mypy"])

    print("Performing static type check...")
    run_command("mypy")


def run_all(args: argparse.Namespace) -> None:
    update_all_packages(args)
    tests(args)
    flake8_check(args)
    run_shellcheck(args)
    py_test_coverage(args)


if __name__ == "__main__":
    ENV["PYTHONPATH"] = str(BASE_DIR)

    parser = argparse.ArgumentParser(
        description="Manager for KiCad Footprint and 3D Model Generator",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (can be specified multiple times)",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="[command]")

    help_parser = subparsers.add_parser("help", help="- This text")

    fmt_chk_parser = subparsers.add_parser(
        "format_check", help="- pycodestyle/black/isort validation"
    )
    fmt_chk_parser.set_defaults(func=format_check)

    flake8_chk_parser = subparsers.add_parser(
        "flake8_check", help="- flake8 validation"
    )
    flake8_chk_parser.set_defaults(func=flake8_check)

    shellchk_parser = subparsers.add_parser(
        "run_shellcheck", help="- Run CI checks for footprint generators"
    )
    shellchk_parser.set_defaults(func=run_shellcheck)

    unit_tests_parser = subparsers.add_parser("unit_tests", help="- Run unit tests")
    unit_tests_parser.set_defaults(func=unit_tests)

    py_test_cvrg_parser = subparsers.add_parser(
        "py_test_coverage", help="- Unit test coverage"
    )
    py_test_cvrg_parser.set_defaults(func=py_test_coverage)

    tests_parser = subparsers.add_parser("tests", help="- Run all tests")
    tests_parser.set_defaults(func=tests)

    updt_pkgs_parser = subparsers.add_parser(
        "update_packages", help="- Check & update production dependency changes"
    )
    updt_pkgs_parser.set_defaults(func=update_packages)

    updt_dev_pkgs_parser = subparsers.add_parser(
        "update_dev_packages",
        help="- Check & update development and production dependency changes",
    )
    updt_dev_pkgs_parser.set_defaults(func=update_dev_packages)

    updt_3d_pkgs_parser = subparsers.add_parser(
        "update_3d_packages",
        help="- Check & update 3d model generator dependency changes",
    )
    updt_3d_pkgs_parser.set_defaults(func=update_3d_packages)

    updt_doc_pkgs_parser = subparsers.add_parser(
        "update_doc_packages",
        help="- Check & update the documentation depencency changes",
    )
    updt_doc_pkgs_parser.set_defaults(func=update_doc_packages)

    updt_all_pkgs_parser = subparsers.add_parser(
        "update_all_packages", help="- Check & update all packages"
    )
    updt_all_pkgs_parser.set_defaults(func=update_all_packages)

    stat_typ_chk_parser = subparsers.add_parser(
        "static_type_check", help="- Run a static type check"
    )
    stat_typ_chk_parser.set_defaults(func=static_type_check)

    run_all_parser = subparsers.add_parser(
        "run_all", help="Run all commands (Testing Only)"
    )
    run_all_parser.set_defaults(func=run_all)

    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose > 1:
        log_level = logging.DEBUG
    elif args.verbose == 1:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)

    if hasattr(args, "func"):
        try:
            args.func(args)
        except DependencyException as e:
            print(f"Dependency Error: {e}")
            exit(1)
        except subprocess.CalledProcessError as e:
            print(
                f"Called Process Error: '{_format_command(e.cmd)}' "
                f"exited with code {e.returncode}"
            )
            exit(e.returncode)
    else:
        parser.print_help()
