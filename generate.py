#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022 Adobe
# All Rights Reserved.
#
# NOTICE: Adobe permits you to use, modify, and distribute this file in
# accordance with the terms of the Adobe license agreement accompanying
# it.

import subprocess
import argparse
from pathlib import Path
import shutil


def parse_args():
    parser = argparse.ArgumentParser(description="Generate documentation for Lagrange.")
    parser.add_argument("path", type=str, help="Path to lagrange repository")
    parser.add_argument(
        "--open",
        action="store_true",
        help="Prepare repo for open-source version of the website",
    )
    return parser.parse_args()


def prepare_open():
    script_dir = Path(__file__).parent.resolve()
    (script_dir / "mkdocs.yml").unlink()
    (script_dir / "mkdocs.open.yml").rename("mkdocs.yml")


def main():
    args = parse_args()
    lagrange_dir = Path(args.path)
    if not lagrange_dir.exists():
        print("Path doesn't exist")

    if args.open:
        prepare_open()

    script_dir = Path(__file__).parent.resolve()

    is_corp = Path(script_dir / "mkdocs.open.yml").exists()

    if is_corp:
        docs_dir = str(script_dir / "docs")
    else:
        docs_dir = str(script_dir / "docs/open")

    # Generates Doxygen C++ documentation
    build_dir = script_dir / "build"
    build_dir.mkdir(exist_ok=True)
    subprocess.run(
        [
            "cmake",
            "-B",
            str(build_dir),
            "-S",
            str(lagrange_dir / "docs/cpp"),
            "-DDOXYGEN_OUTPUT_DIR=" + docs_dir,
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

    # Generates Sphinx Python documentation
    subprocess.run(
        ["make", "-C", str(lagrange_dir / "docs/python"), "html"], check=True
    )
    shutil.copytree(
        lagrange_dir / "docs/python/build/html",
        Path(docs_dir) / "python",
        dirs_exist_ok=True,
    )

    print("run `mkdocs serve` and open http://127.0.0.1:8000/")


if __name__ == "__main__":
    main()
