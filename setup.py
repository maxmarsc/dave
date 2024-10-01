from setuptools import setup, find_packages

setup(
    name="davext",
    version="0.1.1",
    author="maxmarsc",
    install_requires=["matplotlib", "six"],
    extras_require={
        "tests": ["pytest", "librosa>=0.6.0", "pystoi>=0.2.1"],
        "display": ["matplotlib>=2.2.3"],
        "doc": ["sphinx", "sphinx_rtd_theme", "numpydoc"],
    },
    # packages=find_packages(include=["dave", "dave.common" "dave.server.debuggers", "dave.debuggers.lldb", "dave.debuggers.gdb", "dave.debuggers.pdb",
    #                                 "dave.languages.c_cpp", "dave.languages.python"]),
    packages=find_packages(),
    package_data={
        "dave": ["assets/lldb_init.py", "assets/.gdbinit", "assets/.lldbinit"]
    },
    include_package_data=True,
)
