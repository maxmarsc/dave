# DAVE - Debugger Audio Visualization Extension
DAVE is a GDB & LLDB extension which provide commands to visualize audio data
directly from your buffers/classes. No need to recompile your code and/or instrument
it with nasty macros or fancy libs, just start your debugger !

<p align="center">
    <b> DAVE GUI </b>
</p>
<p align="center">
    <img src=".pictures/phase.png">
</p>

Currently supported audio containers (both in `float` and `double`) are :

__1D (mono) containers__:
- `std::array`
- `std::vector`
- `std::span`
- `C array`
- `pointer`

__2D (multichannel) containers__:
- Any nesting of 1D containers
- `juce::AudioBuffer`
- `juce::dsp::AudioBlock`

Currently supported OS are Linux and supposedly MacOS. Both GNU and LLVM stdlib
implementation are supported.

---

To get started first follow the `Project Setup` guide below, then you can read 
the [User Guide](USER_GUIDE.md) to get familiar with DAVE

## Project setup
### Installation
To install dave and its bindings it relatively simple :

---
#### Linux
```bash
# First install the module itself
pip install --user git+ssh://git@github.com/maxmarsc/dave.git@main
# Then install the bindings for your debugger
python -m dave install [gdb|lldb|both]
```

*No need the use the --user flag if installing in a virtual environment*

#### Mac OS
Currently only the toolchain provided by XCode is supported. If you use a custom
toolchain (maybe with CLion), please contact me or open an issue.
```bash
# Install the tcl/tk binding for xcode's python if needed
xcrun python3 -c "import tkinter" || brew install python-tk@$(xcrun python3 --version | grep -oE '[0-9]+\.[0-9]+' | head -n1)
# Install the dave module
xcrun pip3 install --user git+ssh://git@github.com/maxmarsc/dave.git@main
# Install the lldb bindings
xcrun python3 -m dave install lldb
```

---

Then when starting your debugger you should see the following message :
```
[dave] Successfully loaded
```

And the dave commands should be available :
 - `dave show`
 - `dave delete`
 - `dave freeze`
 - `dave concat`

See the [User Guide](USER_GUIDE.md) on how to use these.

### Update
If you want/need to update dave, it's done in two steps :

#### Linux
```bash
# Update the module itself
pip install --user git+ssh://git@github.com/maxmarsc/dave.git@main
# Update the bindings for your debugger
python -m dave update [gdb|lldb|both]
```

#### Mac OS
```bash
xcrun pip3 install --user git+ssh://git@github.com/maxmarsc/dave.git@main
xcrun python3 -m dave update lldb
```

### Uninstallation
**Note:** You can notice the pip package is actually called `davext` and not `dave`
this is because the name `dave` is already taken on pypi, but I don't plan to change.

#### Linux
To remove the dave bindings
```bash
python -m dave uninstall [gdb|lldb|both]
```

You can then also remove the python module if you want : 
```bash
pip uninstall davext
```

#### Mac OS
To remove the dave bindings
```bash
xcrun python3 -m dave uninstall lldb
```

You can then also remove the python module if you want : 
```bash
xcrun pip3 uninstall davext
```
---


## Milestones
- [x] Freeze
- [x] Concatenate 
- [x] Save to disc
- [x] Add tooltip hover for action buttons
- [x] out-of-scope detection
- [x] react to step over/up/down
- [x] Mid/Side
- [x] Interleaved 
- [x] Easy installation
- [x] improve logging system
- [x] document commands
- [x] add license
- [x] llvm libc/libstd (need to be tested)
- [x] JUCE 
- [ ] GSL
- [ ] command aliases
- [ ] minimize call to render functions
- [ ] CHOC 
- [ ] Document the code
- [ ] Add a way for the user to add custom container support
- [ ] find testing strategy
- [ ] Play 
- [x] Restart dave process 
- [x] Improve GUI proportions
- [x] container deletion (GUI + delete command)
- [x] LLDB





## Troubleshooting

### Set logging level
When running into an issue, please activate the debug log level, by setting
the env variable `DAVE_LOGLEVEL` to `debug` before starting the debugger.

### Python support
Python support is extremely limited because both python debuggers I have investigated
(pdb and debugpy) does not provide an API complete enough to provide full DAVE support

Only 1D and 2D numpy tensors are supported, and you need to manually import dave
from the debugger CLI, like this:
```py
import dave.debuggers.pdb as pydave
```

pydave provides two functions :
 - `pydave.show` which display a container
 - `pydave.update` which forces the update of the containers data


### LLDB on Ubuntu 22.04
When starting lldb on ubuntu 22.04 you might get this error :
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
ModuleNotFoundError: No module named 'lldb'
```

This is a [known bug](https://bugs.launchpad.net/ubuntu/+source/llvm-defaults/+bug/1972855). In the meantime you can fix these using a symbolic link :
```bash
sudo mkdir -p /usr/lib/local/lib/python3.10/
sudo ln -s /usr/lib/llvm-${VERSION}/lib/python3.10/dist-packages /usr/lib/local/lib/python3.10/dist-packages
```

### LLDB init
To always load the .lldbinit file in the current working directory, add the following command to ~/.lldbinit:
```
settings set target.load-cwd-lldbinit true
```

### LLDB python module linting
for `venv`
```bash
touch venv/lib64/python3.10/site-packages/lldb.pth
echo "/usr/lib/llvm-${VERSION}/lib/python3.10/dist-packages/" > venv/lib64/python3.10/site-packages/lldb.pth
```