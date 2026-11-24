#!/usr/bin/env python3
"""Prepare an isolated OpenGMK source copy plus a real-data headless probe.

No third-party source or game data is included in this repository. Output must
be a new directory under local-tools/. Does not download, build or package.
"""
import argparse
from pathlib import Path
import shutil
import subprocess

BASE = "9e4282e6d19f4dd00961811840ddc3e11da6dd5a"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    source, output = args.source.resolve(), args.output.resolve()
    if not output.is_relative_to(root / "local-tools") or output.exists():
        parser.error("output must be a NEW directory under this checkout's local-tools/")
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != BASE:
        parser.error(f"expected OpenGMK {BASE}, got {revision}")
    if subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"], text=True).strip():
        parser.error("source must be pristine; use the preserved upstream checkout")
    shutil.copytree(source, output, ignore=shutil.ignore_patterns(".git", "target"))
    manifest = output / "Cargo.toml"
    text = manifest.read_text()
    text = text.replace('members = [', 'members = [\n    "native-probe",', 1)
    manifest.write_text(text)
    probe = output / "native-probe"
    probe.mkdir()
    (probe / "Cargo.toml").write_text('''[package]
name = "howaw-native-probe"
version = "0.1.0"
edition = "2021"
publish = false

[[bin]]
name = "howaw-native-probe"
path = "main.rs"

[dependencies]
gm8exe = { path = "../gm8exe" }
gml-parser = { path = "../gml-parser", features = ["runner-serde-derives"] }
serde = { version = "1.0", features = ["derive"] }
getrandom = "0.2"
rect_packer = "0.2"
''')
    shutil.copyfile(Path(__file__).with_name("native_data_probe.rs"), probe / "main.rs")
    print(f"Prepared {output.relative_to(root)} from {revision}")


if __name__ == "__main__":
    main()
