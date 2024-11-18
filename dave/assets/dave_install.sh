#!/bin/bash
set -euo pipefail

show_help() {
    echo "usage: $(basename "$0") [-h] [-b BRANCH]"
    echo ""
    echo "Installation script for DAVE"
    echo "Users should call it with no arguments to download the stable version"
    echo ""
    printf "options:\n"
    printf "\t-b BRANCH\n"
    printf "\t\t\tDeveloper option :\n"
    printf "\t\t\tWill pip install dave from the given branch, not from pypi\n"
    echo ""
    echo "options:"
    printf "  \t-h, --help\tshow this help message and exit\n"
}

show_intro() {
  echo "Hello ! This is the installation script for dave. First thanks a lot for trying it out"
  echo "Please note that DAVE is still in early development. If you encounter any issue"
  echo "or have any suggestion, please visit https://github.com/maxmarsc/dave"
  echo ""
  echo "I'm working hard to make this project stable HOWEVER if you encounter an issue during or after the installation DON'T PANIC"
  echo "To revert the installation process you can simply follow these commands :"
  printf "\trm -rf ~/.dave     # Will remove the dave environment and its module\n"
  printf "\trm -rf ~/.gdbinit  # Will remove gdb bindings\n"
  printf "\trm -rf ~/.lldbinit # Will remove lldb bindings\n"
  printf "\nIf you don't wanna remove the init files of your debuggers for any reason, just edit out the lines between --- DAVE BEGIN --- and --- DAVE END ---"
  printf "\n\nThis message should disappear soon enough, happy coding !\n\n"

  read -rp "Type Enter to continue" response
}


PIP_SRC="davext"
# Check for dev flag
if [[ "$#" -eq 2 && "$1" == "-b" ]]; then
    PIP_SRC="git+ssh://git@github.com/maxmarsc/dave.git@$2"
    echo "Installing python module from git, for advised developers only"
# Check for help flag
elif  [[ ("$#" -eq 1 && "$1" == "-h") || "$#" -gt 0 ]]; then
    show_help
    exit 1
else
    show_intro
fi



#============================   OS detection   =================================
if [[ "$(uname)" == "Darwin"* ]]; then
    echo "MacOS detected"
elif [[ "$(uname)" == "Linux"* ]]; then
    echo "Linux detected"
else
    echo "ERROR : Unsupported OS $(uname)"
    exit 1
fi


#============================   Python detection   =============================
# Function to compare versions
version_ge() {
    # Compare two versions, return true (0) if version1 >= version2
    IFS='.' read -r -a version1 <<< "$1"
    IFS='.' read -r -a version2 <<< "$2"

    for i in {0..1}; do
        # If version1 is greater than version2
        if [[ ${version1[i]} -gt ${version2[i]} ]]; then
            return 0  # true
        # If version1 is less than version2
        elif [[ ${version1[i]} -lt ${version2[i]} ]]; then
            return 1  # false
        fi
    done
    return 0  # They are equal
}

PY3_VERSIONS=$(compgen -c | grep -E '^python3(\.[0-9]+)?$' | sort -V)
SELECTED_PY3=""
for PY3 in $PY3_VERSIONS; do
    # Check for version
    VERSION="$("$PY3" --version | awk '{print $2}')"
    if ! version_ge "$VERSION" "3.10";then
      continue
    fi

    # Check for venv
    VENV_CHECK_CALL="$PY3 -m venv -h"
    if ! eval "$VENV_CHECK_CALL" > /dev/null 2>&1 ; then
        continue
    fi

    # Check for tkinter
    TKINTER_CHECK_CALL="$PY3 -c 'import tkinter;tkinter.Tk()'"
    if ! eval "$TKINTER_CHECK_CALL" > /dev/null 2>&1 ; then
        continue
    fi

    # Check for TCL version
    TCL_VERSION=$("$PY3" -c "import tkinter;print(tkinter.TclVersion, end='')")
    if version_ge "$TCL_VERSION" "9.0";then
      >&2 echo "Skipping $VERSION because of Tcl version $TCL_VERSION"
      continue
    fi

    SELECTED_PY3="$PY3"
    break
done

if [[ "$SELECTED_PY3" == "" ]];then
  >&2 echo "Failed to find a working python >= 3.10 installation with working venv and tkinter modules"
  if [[ "$(uname)" == ""* ]]; then
        >&2 echo ""
        >&2 echo "On MacOS python>=3.12 installed with Homebrew is known to come with Tcl 9.0 which breaks matplotlib"
        >&2 echo "If you have such an installation I recommend installing a 3.10 or 3.11 version of python-tk"
        >&2 echo "You can install tkinter using homebrew or macports"
        >&2 printf "\tbrew install python-tk@3.10 \nor\n"
        >&2 printf "\tbrew install python-tk@3.11 \nor\n"
        >&2 printf "\tsudo port install py-tkinter # >= 3.10\n"
  fi
  exit 1
fi

echo "Selection $SELECTED_PY3 for dave installation"
echo "With Tcl ${TCL_VERSION}"
echo ""

#============================   DAVE folder   ==================================
# Create dave dir
DAVE_DIR="$HOME"/.dave
if [[ -d "$DAVE_DIR" ]]; then
    # count items in the ~/.dave folder
    ITEM_COUNT=$(find "$DAVE_DIR" -mindepth 1 -maxdepth 1 | wc -l)

    # if the only thing left is the custom_containers folder it's ok
    if [[ $ITEM_COUNT -ne 1 || ! -d "$DAVE_DIR/custom_containers" ]];then
        echo "Previous installation of dave found in $DAVE_DIR. Aborting"
        echo "You're only allowed to keep $DAVE_DIR/custom_containers between installations"
        exit 1
    fi
fi

mkdir -p "$DAVE_DIR"


#============================   DAVE venv   ====================================
# Create the venv
echo "Creating custom dave venv..."
"$SELECTED_PY3" -m venv "$DAVE_DIR/venv"
ACTIVATE_SCRIPT="$HOME/.dave/venv/bin/activate"
# Activate the venv
# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

# Install dave package
echo "Installing dave module..."
pip install "$PIP_SRC"
deactivate


#============================   DAVE command line tool   =======================
# Installing dave bash script
mkdir "$HOME"/.dave/scripts
DAVE_SCRIPT=$(find "$DAVE_DIR"/venv/lib/python3*/site-packages/dave/assets -name "dave")
cp "$DAVE_SCRIPT" "$DAVE_DIR"/scripts

# Add dave scripts to PATH
# shellcheck disable=SC2016
PATH_COMMAND='export PATH="$PATH:$HOME"/.dave/scripts'

zsh_path_install() {
    printf "\nAllowing ZSH to access dave commands requires adding "
    printf "'~/.dave/scripts' to the PATH in ~/.zshrc\n"
    printf "\t"
    read -rp "Allow ~/.zshrc modification ? [Y/n]: " response
    response=${response:-y}  # Set default to 'y' if no input is provided

    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        # Check if the command already exists in ~/.zshrc
        if ! grep -Fxq "$PATH_COMMAND" ~/.zshrc; then
            echo "$PATH_COMMAND" >> ~/.zshrc
            echo "Added to ~/.zshrc: $PATH_COMMAND"
        else
            echo "The command is already present in ~/.zshrc. Skipping"
        fi
    else
        echo "Skipping ~/.zshrc"
    fi
}

bash_path_install() {
    printf "\nAllowing BASH to access dave commands requires adding "
    printf "'~/.dave/scripts' to the PATH in ~/.bashrc\n"
    printf "\t"
    read -rp "Allow ~/.bashrc modification ? [Y/n]: " response
    response=${response:-y}  # Set default to 'y' if no input is provided

    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        # Check if the command already exists in ~/.zshrc
        if ! grep -Fxq "$PATH_COMMAND" ~/.bashrc; then
            echo "$PATH_COMMAND" >> ~/.bashrc
            echo "Added to ~/.bashrc: $PATH_COMMAND"
        else
            echo "The command is already present in ~/.bashrc. Skipping"
        fi
    else
        echo "Skipping ~/.bashrc"
    fi
}

automatic_bind() {
    # shellcheck disable=SC1090
    source "$ACTIVATE_SCRIPT"

    # propose to bind gdb if installed
    if command -v gdb > /dev/null 2>&1; then
        printf "\ngdb was detected on your system\n"
        read -rp "Would you like to bind dave to gdb ? [Y/n]: " response
        response=${response:-y}
        if [[ "$response" == "y" || "$response" == "Y" ]]; then
            python -m dave bind gdb
        fi
    fi

    # propose to bind lldb if installed
    if command -v lldb > /dev/null 2>&1; then
        printf "\nlldb was detected on your system\n"
        read -rp "Would you like to bind dave to lldb ? [Y/n]: " response
        response=${response:-y}
        if [[ "$response" == "y" || "$response" == "Y" ]]; then
            python -m dave bind lldb
        fi
    fi

    deactivate
}

SHELL_NAME=$(basename "$SHELL")
if [[ "$(uname)" == "Darwin"* ]]; then
    zsh_path_install
    bash_path_install
elif [[ "$(uname)" == "Linux"* ]]; then
    if [[ "$SHELL_NAME" == "zsh" ]]; then
        zsh_path_install
    fi
    bash_path_install
fi

automatic_bind

echo ""
echo "DAVE was successfully installed. To access the dave shell command, source your .bashrc/.zshrc file"
echo ""
echo "Don't forget to check the User Guide : https://github.com/maxmarsc/dave/blob/main/USER_GUIDE.md"