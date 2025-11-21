# DAVE development guide
This is a guide to help setup a development environment for DAVE

## Venv setup
DAVE base itself on the use of a `venv` virtual environment, in order to use a development
folder proceed as follow : 

1. Create a python virtual environment using `venv` : `python -m venv .venv`
2. Activate the virtual environment `source .venv/bin/activate`
3. Install DAVE in dev mode : `pip install -e .`
4. Bind your debugger(s) to dave : `python -m dave bind`
5. Export the `DAVE_VENV_FOLDER` env variable to indicate your venv path : `export DAVE_VENV_FOLDER="$(pwd)/.venv"`

You should be good to go ! Now when starting your debugger, it should use the 
python files in your git folder and not the use installed by the `dave_install.sh`
script.

## Examples compilation
### C/C++
```bash
cmake -B build -S examples/c_cpp
```

### Rust
```bash
cargo build --manifest-path examples/rust/Cargo.toml
```


## common/server/client
Both LLDB and GDB uses a python intepreter to provide a python API. Depending
on your system, there's almost no garranties given on the used python interpreter.

To support this lack of garranties, DAVE is designed with the following principles :
1. the `server` submodule contains code used by the debugger
2. the `common` submodule contains code used by the debugger AND the gui
3. the `client` submodule contains code used by the gui

Both `server` and `common` must only contain **Python~=3.9 vanilla code** to provide
full compatibility with whatever python interpreter your debugger decides to use.

## Pypi packaging
Additional requirements :
```bash
pip install wheel twine
```

Then follow the workflow :
```bash
python setup.py bdist_wheel
# First test on pypi.test
python -m twine upload --repository pypi dist/*
```