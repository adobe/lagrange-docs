#!/usr/bin/env python

# Copyright 2022 Adobe
# All Rights Reserved.
#
# NOTICE: Adobe permits you to use, modify, and distribute this file in
# accordance with the terms of the Adobe license agreement accompanying
# it.

import argparse
import base64
import netrc
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


JAVASCRIPT_REGISTRY = (
    "https://artifactory-uw2.adobeitc.com/artifactory/api/npm/npm-adobe-release/"
)


def javascript_install_env():
    registry = urlsplit(JAVASCRIPT_REGISTRY)
    prefix = f"npm_config_//{registry.netloc}{registry.path}:"
    env = os.environ.copy()
    auth_keys = {f"{prefix}_auth".lower(), f"{prefix}_authToken".lower()}
    # Jenkins already supplies registry-scoped authentication.
    if any(key.lower() in auth_keys and value for key, value in env.items()):
        return env

    # pnpm does not read .netrc itself. Only use this registry's explicit entry;
    # do not fall back to credentials from a default or a different machine.
    netrc_file = Path.home() / "_netrc" if os.name == "nt" else None
    try:
        credentials = netrc.netrc(netrc_file).hosts.get(registry.hostname)
    except FileNotFoundError:
        credentials = None
    except netrc.NetrcParseError:
        # Parser diagnostics can contain file contents, so do not echo them.
        raise RuntimeError(
            "Cannot read Artifactory credentials: check your .netrc syntax and permissions."
        ) from None
    if not credentials or not credentials[0] or not credentials[2]:
        raise RuntimeError(
            f"Add a machine entry for {registry.hostname} with login and password "
            "to ~/.netrc (~/_netrc on Windows)."
        )

    username, _, password = credentials
    auth = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
    env[f"{prefix}_auth"] = auth
    return env


def generate_javascript(script_dir, docs_dir):
    subprocess.run(
        ["pnpm", "install", "--ignore-scripts", "--no-frozen-lockfile"],
        cwd=script_dir,
        env=javascript_install_env(),
        check=True,
    )
    subprocess.run(
        [
            "pnpm",
            "run",
            "docs:javascript",
            "--out",
            str(Path(docs_dir) / "javascript"),
        ],
        cwd=script_dir,
        check=True,
    )


def generate_cpp(script_dir, lagrange_dir, docs_dir):
    build_dir = script_dir / "build"
    build_dir.mkdir(exist_ok=True)
    subprocess.run(
        [
            "cmake",
            "-B",
            str(build_dir),
            "-S",
            str(lagrange_dir / "docs/cpp"),
            "-DDOXYGEN_OUTPUT_DIR=" + str(docs_dir),
            "-DDOXYGEN_OUTPUT_HTML=cpp",
        ],
        check=True,
    )
    subprocess.run(
        [
            "cmake",
            "--build",
            str(build_dir),
            "--target",
            "doc",
        ],
        check=True,
    )


def generate_python(lagrange_dir, docs_dir):
    subprocess.run(
        ["make", "-C", str(lagrange_dir / "docs/python"), "html"], check=True
    )
    shutil.copytree(
        lagrange_dir / "docs/python/build/html",
        docs_dir / "python",
        dirs_exist_ok=True,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Generate documentation for Lagrange.")
    parser.add_argument(
        "targets",
        nargs="+",
        choices=("js", "py", "cpp"),
        help="References to generate: js (TypeDoc), py (Sphinx), cpp (Doxygen)",
    )
    parser.add_argument(
        "--path",
        type=Path,
        metavar="LAGRANGE_ROOT",
        help="Path to the Lagrange repository (required for py and cpp)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Prepare repo for open-source version of the website",
    )
    args = parser.parse_args()
    if args.open and "js" in args.targets:
        parser.error(
            "The js target is internal-only and cannot be combined with --open"
        )
    if {"py", "cpp"} & set(args.targets) and args.path is None:
        parser.error("--path is required for the py and cpp targets")
    return args


def main():
    args = parse_args()
    script_dir = Path(__file__).parent.resolve()

    # The public export only has mkdocs.yaml. In this repository, --open
    # selects the output location without renaming or deleting configuration.
    is_corp = not args.open and (script_dir / "mkdocs.open.yml").exists()
    if "js" in args.targets and not is_corp:
        raise SystemExit("JavaScript reference generation is internal-only.")

    docs_dir = script_dir / ("docs" if is_corp else "docs/open")
    lagrange_dir = args.path.resolve() if args.path is not None else None
    if lagrange_dir is not None and not lagrange_dir.is_dir():
        raise SystemExit(f"Lagrange source directory does not exist: {lagrange_dir}")

    for target in args.targets:
        if target == "js":
            generate_javascript(script_dir, docs_dir)
        elif target == "py":
            generate_python(lagrange_dir, docs_dir)
        elif target == "cpp":
            generate_cpp(script_dir, lagrange_dir, docs_dir)

    task = "-e open serve-open" if args.open else "serve"
    print(f"run `pixi run {task}` and open http://127.0.0.1:8000/")


if __name__ == "__main__":
    main()
