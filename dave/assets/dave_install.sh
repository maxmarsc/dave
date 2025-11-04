#!/bin/bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'  
NC='\033[0m'           # No Color (reset to default)

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
  echo -e "${GREEN}"
  echo "Hello ! This is the installation script for dave. First thanks a lot for trying it out"
  echo "Please note that DAVE is still in early development. If you encounter any issue"
  echo "or have any suggestion, please visit https://github.com/maxmarsc/dave"
  echo ""
  echo -e "${YELLOW}"
  echo "I'm working hard to make this project stable HOWEVER if you encounter an issue during or after the installation DON'T PANIC"
  echo "To revert the installation process you can simply follow these commands :"
  printf "\trm -rf ~/.dave     # Will remove the dave environment and its module\n"
  printf "\trm -rf ~/.gdbinit  # Will remove gdb bindings\n"
  printf "\trm -rf ~/.lldbinit # Will remove lldb bindings\n"
  printf "\nIf you don't wanna remove the init files of your debuggers for any reason, just edit out the lines between --- DAVE BEGIN --- and --- DAVE END ---"
  printf "\n\nThis message should disappear soon enough, happy coding !\n\n"
  echo -e "${NC}"

  read -rp "Type Enter to continue" response
}


PIP_SRC="davext"
# Check for dev flag
if [[ "$#" -eq 2 && "$1" == "-b" ]]; then
    PIP_SRC="git+ssh://git@github.com/maxmarsc/dave.git@$2"
    echo -e "${YELLOW}"
    echo "Installing python module from git, for advised developers only"
    echo -e "${NC}"
# Check for help flag
elif  [[ ("$#" -eq 1 && "$1" == "-h") || "$#" -gt 0 ]]; then
    show_help
    exit 1
else
    show_intro
fi



#============================   OS detection   =================================
if [[ "$(uname)" == "Darwin"* ]]; then
    echo -e "${GREEN}"
    echo "MacOS detected"
    echo -e "${NC}"
elif [[ "$(uname)" == "Linux"* ]]; then
    echo -e "${GREEN}"
    echo "Linux detected"
    echo -e "${NC}"
else
    echo -e "${RED}"
    echo "ERROR : Unsupported OS $(uname)"
    echo -e "${NC}"
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

    SELECTED_PY3="$PY3"
    break
done

if [[ "$SELECTED_PY3" == "" ]];then
  echo -e "${RED}"
  >&2 echo "Failed to find a working python >= 3.10 installation with a working venv module"
  echo -e "${NC}"
  exit 1
fi

echo -e "${GREEN}"
echo "Selected $SELECTED_PY3 for dave installation"
echo -e "${NC}"
echo ""

#============================   DAVE folder   ==================================
# Create dave dir
DAVE_DIR="$HOME"/.dave
if [[ -d "$DAVE_DIR" ]]; then
    # count items in the ~/.dave folder
    ITEM_COUNT=$(find "$DAVE_DIR" -mindepth 1 -maxdepth 1 | wc -l)

    # if the only thing left is the custom folder it's ok
    if [[ $ITEM_COUNT -ne 1 || ! -d "$DAVE_DIR/custom" ]];then
        echo -e "${RED}"
        echo "Previous installation of dave found in $DAVE_DIR. Aborting"
        echo "You're only allowed to keep $DAVE_DIR/custom between installations"
        echo -e "${NC}"
        exit 1
    fi
fi

mkdir -p "$DAVE_DIR"


#============================   DAVE venv   ====================================
# Create the venv
echo -e "${GREEN}"
echo "Creating custom dave venv..."
echo -e "${NC}"
"$SELECTED_PY3" -m venv "$DAVE_DIR/venv"
ACTIVATE_SCRIPT="$HOME/.dave/venv/bin/activate"
# Activate the venv
# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

# Install dave package
echo -e "${GREEN}"
echo "Installing dave module..."
echo -e "${NC}"
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
            echo -e "${GREEN}"
            echo "Added to ~/.zshrc: $PATH_COMMAND"
            echo -e "${NC}"
        else
            echo -e "${YELLOW}"
            echo "The command is already present in ~/.zshrc. Skipping"
            echo -e "${NC}"
        fi
    else
        echo -e "${GREEN}"
        echo "Skipping ~/.zshrc"
        echo -e "${NC}"
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
            echo -e "${GREEN}"
            echo "Added to ~/.bashrc: $PATH_COMMAND"
            echo -e "${NC}"
        else
            echo -e "${YELLOW}"
            echo "The command is already present in ~/.bashrc. Skipping"
            echo -e "${NC}"
        fi
    else
        echo -e "${GREEN}"
        echo "Skipping ~/.bashrc"
        echo -e "${NC}"
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
echo -e "${GREEN}"
echo "DAVE was successfully installed. To access the dave shell command, source your .bashrc/.zshrc file"
echo ""
echo "Don't forget to check the User Guide : https://github.com/maxmarsc/dave/blob/main/USER_GUIDE.md"
echo -e "${NC}"