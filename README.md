# dave
Debugger Audio Visualization Extension

## Installation
To install dave and its bindings it relatively simple :
```bash
# First install the module itself
git clone git@github.com:maxmarsc/gave.git
pip install -e gave
# Then install the bindings for your debugger
python -m gave install [gdb|lldb|both]
```

Then when starting your debugger you should see the following message :
```
[dave] Successfully loaded
```

And the dave commands should be available :
 - `gave show`
 - `gave delete`
 - `gave freeze`
 - `gave concat`

## Update
If you want/need to update dave, it's done in two steps :
```bash
# Update the module itself
pip install --upgrade gave
# Update the bindings for your debugger
python -m gave update [gdb|lldb|both]
```

## Uninstallation
To remove the dave bindings
```bash
python -m gave uninstall [gdb|lldb|both]
```

You can then also remove the python module if you want : 
```bash
pip uninstall gave
```

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
- [ ] Rename every `gave` to `dave`
- [ ] command aliases
- [ ] minimize call to render functions
- [ ] llvm libc/libstd
- [ ] GSL
- [ ] JUCE 
- [ ] CHOC 
- [ ] improve logging system
- [ ] Document the code
- [ ] add setup instructions to readme
- [ ] add license
- [ ] add better documentation to GDB command
- [ ] find testing strategy
- [ ] Play 
- [x] Restart dave process 
- [x] Improve GUI proportions
- [x] container deletion (GUI + delete command)
- [x] LLDB



## Troubleshooting

### Python support
Python support is extremely limited because both python debuggers I have investigated
(pdb and debugpy) does not provide an API complete enough to provide full DAVE support

Only 1D and 2D numpy tensors are supported, and you need to manually import dave
from the debugger CLI, like this:
```py
import gave.debuggers.pdb as pygave
```

pygave provides two functions :
 - `pygave.show` which display a container
 - `pygave.update` which forces the update of the containers data


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