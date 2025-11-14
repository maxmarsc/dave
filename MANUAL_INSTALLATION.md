# Manually installing DAVE

This is a guide on how to install DAVE manually for those of you who don't sure
an installation bash script (can't blame you) or like to play with things.

*This guide should be up to date with the automatic installation procedure, but*
*when in doubt check the [installation script](./dave/assets/dave_install.sh)*

## Requirements
All you require for installing DAVE is a working Python >= 3.10 installation
with the `venv` module.

In the next BASH snippets we will refer to this python executable as `PYTHON`

### 1. Create the DAVE folder and venv
In order for DAVE to:
1. Have its code isolated from the rest of your system
2. Make sure the debugger always find DAVE

```bash
mkdir ~/.dave                 # Create DAVE folder
PYTHON -m venv ~/.dave/venv   # Create DAVE venv
```

### 2. Install DAVE in the venv
```bash
source activate ~/.dave/venv/bin/activate
pip install davext
deactivate
```

### 3. Install the DAVE CLI tool to manage your installation
The DAVE cli tool is helpful to update DAVE and manage debugger bindings

You just need to add its directory to you PATH
```bash
# You should add this to your .bashrc/.zshrc/.whatever
export PATH="$PATH:$HOME"/.dave/scripts
```

### 4. Bind DAVE to your debugger
Use the DAVE CLI tool to make your your favorite debugger loads DAVE automatically

```bash
# gdb
dave bind gdb

# lldb
dave bind lldb

# both
dave bind
```