# dave
Debugger Audio Visualization Extension

## Milestones
- [ ] Mid/Side 
- [ ] LLDB
- [ ] Freeze 
- [ ] Concatenate 
- [ ] Play 
- [ ] Restart dave process 
- [ ] GSL 
- [ ] JUCE 
- [ ] CHOC 
- [ ] One liner BASH installation 
- [ ] Improve GUI proportions
- [ ] Save to disc
- [ ] llvm libc/libstd
- [ ] container deletion (GUI + delete command)
- [ ] out-of-scope detection
- [ ] add setup instructions to readme
- [ ] add license
- [ ] improve logging system

## Python support
```py
import gave.debuggers.pdb as pygave
```


## Troubleshooting
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