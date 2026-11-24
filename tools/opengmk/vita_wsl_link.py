#!/usr/bin/env python3
"""Use an existing WSL hard-float VitaSDK linker from Windows Rust.

Set CARGO_TARGET_ARMV7_SONY_VITA_NEWLIBEABIHF_LINKER to a .cmd that invokes
this script with %*. No shell commands, installation, packaging or device I/O.
VITA_WSL_SDK optionally selects a read-only SDK path inside WSL.
"""
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys


def translate(arg):
    return re.sub(r"([A-Za-z]):[\\/]", lambda m: "/mnt/" + m[1].lower() + "/", arg).replace("\\", "/")


def main():
    args = []
    for arg in sys.argv[1:]:
        if arg.startswith("@"):
            # rustc's GNU response files use shell-style quoting, not cmd syntax.
            content = Path(arg[1:]).read_text(encoding="utf-8")
            args.extend(shlex.split(content))
        else:
            args.append(arg)
    sdk = os.environ.get("VITA_WSL_SDK", "/usr/local/vitasdk-hardfp")
    command = ["wsl", "-d", os.environ.get("VITA_WSL_DISTRO", "Ubuntu"), "--exec",
               sdk + "/bin/arm-vita-eabi-gcc", "-mfloat-abi=hard"]
    command.extend(translate(arg) for arg in args)
    return subprocess.call(command)


if __name__ == "__main__":
    sys.exit(main())
