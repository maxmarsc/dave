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
cmake -B build_cpp -S examples/c_cpp
```

### Rust
```bash
CARGO_TARGET_DIR="build_rust" cargo build --manifest-path examples/rust/Cargo.toml
```

## Testing
For now only the code running on the server side (the debugger, not the gui) is tested

### Server testing
#### Environment variable
You can use the following environment variables to control the tests
- `FILTER="pattern"`: run only the test with `pattern` in their name
- `C_CPP_BIN_DIR`: Required if executing the C/C++ tests. Must be set to the folder
containing the test binaries.
- `RUST_BIN_DIR`: Required if executing the Rust tests. Must be set to the folder
containing the test binaries.

#### Run the tests
To run all tests for a set of versions of GDB/LLDB run:
```bash
# First build the C/C++ binaries
cmake -B build_c_cpp -G Ninja -DCMAKE_BUILD_TYPE=Debug -DDAVE_BUILD_TESTS=ON -DDAVE_BUILD_EXAMPLES=OFF -S examples/c_cpp
cmake --build build_c_cpp --target all
# Then build the RUST binaries
CARGO_TARGET_DIR="build_rust" cargo build --manifest-path examples/rust/Cargo.toml

# Set the env
export C_CPP_BIN_DIR="$(pwd)/build_c_cpp" 
export RUST_BIN_DIR="$(pwd)/build_rust/debug"

# Run GDB tests
gdb -q --batch -nx -x tests/server/gdb_testing/run_tests.py

# Run LLDB tests
lldb -b -x -o 'command script import tests/server/lldb_testing/run_tests.py'
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
