# Debugger Audio Visualization Extension
![logo](.pictures/dave_logo_long_v6.png  )

DAVE is a GDB & LLDB extension which provide commands to visualize audio data
directly from your buffers/classes. No need to recompile your code and/or instrument
it with nasty macros or fancy libs, just start your debugger !

<p align="center">
    <b> The DAVE GUI </b>
</p>
<p align="center">
    <img src=".pictures/gui_demo.png">
</p>

Currently supported audio containers (both in `float` and `double`) are :

__1D (mono) containers__:
- `std::array`
- `std::vector`
- `std::span`
- [Microsoft's `gsl::span`](https://github.com/microsoft/GSL/blob/main/include/gsl/span) 
- `C array`
- `pointer`
- `choc::buffer::MonoView`
- `choc::buffer::MonoVBuffer`

__2D (multichannel) containers__:
- Any nesting of C/C++ standards 1D containers
- `juce::AudioBuffer`
- `juce::dsp::AudioBlock`
- `choc::buffer::InterleavedView`
- `choc::buffer::InterleavedBuffer`
- `choc::buffer::ChannelArrayView`
- `choc::buffer::ChannelArrayBuffer`


### Current support
| Operating System  | Status       |
|-------------------|--------------|
| Linux             | ✅           |
| MacOS             | ✅ (python 3.10/3.11 only)        |
| Windows           | ❌           |

| Debugger platform | GDB          | LLDB         |
|-------------------|--------------|--------------|
| CLI               | ✅           | ✅           |
| VSCode            | ✅ (update on frame broken) | ❓ need testing  |
| CLion             | ✅ (update on frame broken) | ✅ (update on frame broken) |
| XCode             | ❓ need testing             | ❓ need testing |
| Visual Studio      | ❌           | ❌           |

*update on frame broken* means DAVE is not able to react to frame change happening
through the IDE ui

---

To get started first follow the `Project Setup` guide below, then you can read 
the [User Guide](USER_GUIDE.md) to get familiar with DAVE.

If you want to develop/experiment with dave, follow the [Development Guide](DEV_GUIDE.md)

## Project setup
### Requirements
DAVE requires a python >= 3.10 installation with working `venv` and `tkinter` modules

### Installation
The simplest way to install dave and its bindings is to use the install script :
```bash
# via the install script
## using curl
bash -c "$(curl -fsSL https://raw.githubusercontent.com/maxmarsc/dave/refs/heads/main/dave/assets/dave_install.sh)"

## using wget
bash -c "$(wget https://raw.githubusercontent.com/maxmarsc/dave/refs/heads/main/dave/assets/dave_install.sh -O -)"
```

It will install the python dave modules, the debuggers bindings, and the `dave`
cli tool to help manage your dave installation.

*MacOS* : On MacOS distribution you might need to install tkinter using homebrew/macports.
*Python* : Python support is limited and requires a different installation method, see the section below

---

After binding, starts your debugger, you should see the following message :
```
[dave] Successfully loaded
```

And the dave debugger commands should be available :
 - `dave show`
 - `dave delete`
 - `dave freeze`
 - `dave concat`

See the [User Guide](USER_GUIDE.md) on how to use these.

### Update
If you want/need to update dave, you can use the `dave` cli tool :

```bash
# Update dave
dave update
```

### Uninstallation
If you just want to remove the dave bindings run
```bash
dave unbind
```

If you want to completely remove dave from your system run
```bash
dave uninstall
```

### Python support
Python support is limited because both python debuggers I have investigated
(pdb and debugpy) does not provide an API complete enough to provide full DAVE support.
Most importantly **Python debugger does not provide automatic update on breakpoints**.

To install DAVE for python, install the `davext` pypi package in your environment.

Only 1D and 2D numpy tensors are supported, and you need to manually import dave
from the debugger CLI, like this:
```py
import dave.debuggers.pdb as pydave
```

Then you can use the following commands :
 - `pydave.show` analog to `dave show`
 - `pydave.concat` analog to `dave concat`
 - `pydave.freeze` analog to `dave freeze`
 - `pydave.delete` analog to `dave delete`
 - `pydave.update` which forces the update of the containers data


---


## Licensing
This project is licensed under GPLv3.0. The goal is for you to be able to use it
to debug any project, open or proprietary, but to prevent anyone from making a
proprietary project out of DAVE's code.

If you have any question or request about licensing, don't hesitate to ask !

**Wikipedia:** *Software under the GPL may be run for all purposes, including commercial purposes and even as a tool for creating proprietary software, such as when using GPL-licensed compilers.*

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
- [x] GSL
- [x] Add samplerate support
- [x] Add a way for the user to add custom container support
- [x] Add command to help diagnostic type for custom container support
- [ ] Add argument parsing to `show` (view, layout, settings...)
- [ ] find testing strategy
- [ ] Add versionning selection to dave_install
- [ ] command aliases
- [ ] minimize call to render functions
- [ ] Eigen
- [ ] Add FISH shell support
- [x] CHOC
- [x] Document the code
- [x] Restart dave process 
- [x] Improve GUI proportions
- [x] container deletion (GUI + delete command)
- [x] LLDB





## Troubleshooting

### Set logging level
When running into an issue, please activate the debug log level, by setting
the env variable `DAVE_LOGLEVEL` to `debug` before starting the debugger.

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