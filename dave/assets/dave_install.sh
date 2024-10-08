#!/bin/bash
set -euo pipefail

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


if [[ "$(uname)" == "Darwin"* ]]; then
    echo "MacOS detected"
elif [[ "$(uname)" == "Linux"* ]]; then
    echo "Linux detected"
else
    echo "ERROR : Unsupported OS $(uname)"
    exit 1
fi

# Create dave dir
DAVE_DIR="$HOME"/.dave
if [[ -d "$DAVE_DIR" ]]; then
    echo "$DAVE_DIR folder already exists. Aborting"
    exit 1
fi

mkdir -p "$DAVE_DIR"

# Check for venv
VENV_CHECK_CALL="python3 -m venv -h"
if ! eval "$VENV_CHECK_CALL" > /dev/null 2>&1 ; then
    >&2 echo "'python3 -m venv' command check failed. Check you python3 venv installation" 
    exit 1
fi

# Check for tkinter
TKINTER_CHECK_CALL="python3 -c 'import tkinter;tkinter.Tk()'"
if ! eval "$TKINTER_CHECK_CALL" > /dev/null 2>&1 ; then
    >&2 echo "tkinter check failed. Check your tkinter installation"
    if [[ "$(uname)" == "Darwin"* ]]; then
        >&2 echo "On MacOS you can install tkinter using homebrew or macports"
        >&2 printf "\tbrew install python-tk\n\tor"
        >&2 printf "\tsudo port install py-tkinter"
    fi
fi

# Create the venv
echo "Creating custom dave venv..."
python3 -m venv "$DAVE_DIR/venv"
ACTIVATE_SCRIPT="$HOME/.dave/venv/bin/activate"
# Activate the venv
# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

# Install dave package
echo "Installing dave module..."
pip install davext
deactivate
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
    read -rp "Allow ~/.zshrc modification ? [y/n] (default: y): " response
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
    read -rp "Allow ~/.bashrc modification ? [y/n] (default: y): " response
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
        read -rp "Would you like to bind dave to gdb ? [y/n] (default: y): " response
        response=${response:-y}
        if [[ "$response" == "y" || "$response" == "Y" ]]; then
            python -m dave bind gdb
        fi
    fi

    # propose to bind lldb if installed
    if command -v lldb > /dev/null 2>&1; then
        printf "\nlldb was detected on your system\n"
        read -rp "Would you like to bind dave to lldb ? [y/n] (default: y): " response
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

echo "DAVE was successfully installed. To access the dave shell command, source your .bashrc/.zshrc file"
echo "Don't forget to check the User Guide : https://github.com/maxmarsc/dave/blob/main/USER_GUIDE.md"