import argparse
import subprocess
import pathlib
import sys
import shutil
import tempfile
from typing import List
import logging
import os

LOGLEVEL = os.environ.get("DAVE_LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(levelname)s: %(message)s")


HOME = pathlib.Path.home()

# Dest files
DAVE_FOLDER = HOME / ".dave"
GDB_INIT = HOME / ".gdbinit"
LLDB_INIT = HOME / ".lldbinit"
LLDB_INIT_SCRIPT = DAVE_FOLDER / "lldb_init.py"

# Source files
ASSETS_DIR = pathlib.Path(__file__).parent / "assets"
GDB_INIT_SRC = ASSETS_DIR / ".gdbinit"
LLDB_INIT_SRC = ASSETS_DIR / ".lldbinit"
LLDB_INIT_SCRIPT_SRC = ASSETS_DIR / "lldb_init.py"

BEGIN_MARKER = "# --- DAVE BEGIN ---"
END_MARKER = "# --- DAVE END ---"


# def file_contains_lines(file_path: pathlib.Path, lines_to_check: List[str]) -> int:
#     """
#     Search for a sequence of lines in a file.

#     If found, this returns the line number of the start of the sequence. If not
#     found this return -1
#     """
#     with open(file_path, "r") as file:
#         rlines = file.readlines()
#         num_lines = len(lines_to_check)

#         for i, first_line in enumerate(rlines):
#             # Search for the first line of the sequence
#             if first_line.strip() == lines_to_check[0].strip():
#                 print
#                 # Search for the whole sequence
#                 if all(
#                     [
#                         lines_to_check[y].strip()
#                         == rlines[i : i + num_lines][y].strip()
#                         for y in range(num_lines)
#                     ]
#                 ):
#                     return i
#     return -1


def find_line(file_path: pathlib.Path, line_to_search: str) -> int:
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            if line.strip() == line_to_search.strip():
                return i

    return -1


def delete_lines_from_file(file_path: pathlib.Path, start_line: int, num_lines: int):
    """
    Deletes num_lines from the given file, starting at start_line
    """
    with open(file_path, "r+") as file:
        rlines = file.readlines()
        file.seek(0)
        file.writelines(rlines[:start_line])
        file.writelines(rlines[start_line + num_lines :])
        file.truncate()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Helper script to install LLDB/GDB bindings for DAVE"
    )
    parser.add_argument(
        "action",
        type=str,
        choices=["bind", "unbind", "update", "check"],
        help="Action to perform",
    )
    parser.add_argument(
        "debugger",
        type=str,
        choices=["lldb", "gdb", "both"],
        nargs="?",
        default="both",
        help="Which debugger apply bindings to. Default to 'both'",
    )

    return parser.parse_args()


def check_for_lldb_installation() -> bool:
    if not DAVE_FOLDER.is_dir():
        return False
    elif not LLDB_INIT_SCRIPT.is_file():
        return False
    elif not LLDB_INIT.is_file():
        return False

    # Check content of .lldbinit
    if find_line(LLDB_INIT, BEGIN_MARKER) == -1:
        return False

    return True


def check_for_gdb_installation() -> bool:
    if not DAVE_FOLDER.is_dir():
        return False
    elif not GDB_INIT.is_file():
        return False

    # Check content of .gdbinit
    if find_line(GDB_INIT, BEGIN_MARKER) == -1:
        return False

    return True


def install_lldb(backup=True):
    if not DAVE_FOLDER.is_dir():
        logging.debug(f"Missing {DAVE_FOLDER}, creating")
        DAVE_FOLDER.mkdir()

    if not LLDB_INIT_SCRIPT.is_file():
        logging.debug(f"Missing {LLDB_INIT_SCRIPT}, creating")
        shutil.copy(LLDB_INIT_SCRIPT_SRC, LLDB_INIT_SCRIPT)

    with open(LLDB_INIT_SRC, "r") as lldb_init_src:
        lldb_init_lines = lldb_init_src.readlines()

    if LLDB_INIT.is_file() and backup:
        backup_file(LLDB_INIT)

    with open(LLDB_INIT, "a") as lldb_init:
        lldb_init.writelines(lldb_init_lines)


def backup_file(filepath: pathlib.Path):
    backup = str(filepath) + ".davebak"
    shutil.copy(filepath, backup)
    logging.info(f"Made a backup of {filepath} in {backup}")


def uninstall_lldb(backup=True):
    if backup:
        backup_file(LLDB_INIT)

    start = find_line(LLDB_INIT, BEGIN_MARKER)
    end = find_line(LLDB_INIT, END_MARKER)
    delete_lines_from_file(LLDB_INIT, start, end - start + 1)

    LLDB_INIT_SCRIPT.unlink()


def install_gdb(backup=True):
    if not DAVE_FOLDER.is_dir():
        logging.debug(f"Missing {DAVE_FOLDER}, creating")
        DAVE_FOLDER.mkdir()

    with open(GDB_INIT_SRC, "r") as gdb_init_src:
        gdb_init_lines = gdb_init_src.readlines()

    if GDB_INIT.is_file() and backup:
        backup_file(GDB_INIT)

    with open(GDB_INIT, "a") as gdb_init:
        gdb_init.writelines(gdb_init_lines)


def uninstall_gdb(backup=True):
    if backup:
        backup_file(GDB_INIT)

    start = find_line(GDB_INIT, BEGIN_MARKER)
    end = find_line(GDB_INIT, END_MARKER)
    delete_lines_from_file(GDB_INIT, start, end - start + 1)


def main():
    args = parse_arguments()

    if args.action == "bind":

        if args.debugger in ("gdb", "both"):
            if check_for_gdb_installation():
                logging.warning("GDB bindings are already installed. Skipping")
            else:
                install_gdb()
                logging.info("GDB bindings were installed")

        if args.debugger in ("lldb", "both"):
            if check_for_lldb_installation():
                logging.warning("LLDB bindings are already installed. Skipping")
            else:
                install_lldb()
                logging.info("LLDB bindings were installed")

    elif args.action == "unbind":

        if args.debugger in ("gdb", "both"):
            if check_for_gdb_installation():
                uninstall_gdb()
                logging.info("GDB bindings were uninstalled")
            else:
                logging.error("GDB bindings are not installed")

        if args.debugger in ("lldb", "both"):
            if check_for_lldb_installation():
                uninstall_lldb()
                logging.info("LLDB bindings were uninstalled")
            else:
                logging.error("LLDB bindings are not installed")

    elif args.action == "update":

        if args.debugger in ("gdb", "both"):
            if check_for_gdb_installation():
                uninstall_gdb()
                install_gdb(False)
                logging.info("GDB bindings were updated")
            else:
                logging.error(
                    "Could not update GDB bindings as these are not installed"
                )

        if args.debugger in ("lldb", "both"):
            if check_for_lldb_installation():
                uninstall_lldb()
                install_lldb(False)
                logging.info("LLDB bindings were updated")
            else:
                logging.error(
                    "Could not update LLDB bindings as these are not installed"
                )
    elif args.action == "check":
        if args.debugger == "both":
            raise NotImplementedError()
        elif args.debugger == "lldb":
            if check_for_lldb_installation():
                print(1)
            else:
                print(0)
        else:
            if check_for_gdb_installation():
                print(1)
            else:
                print(0)
            
    else:
        raise NotImplementedError()


if __name__ == "__main__":
    main()
