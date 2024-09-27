from setuptools import setup, find_packages

setup(
    name="davext",
    version="0.1.1",
    author="maxmarsc",
    install_requires=[
        "matplotlib",
    ],
    extras_require={
        "tests": ["pytest", "librosa>=0.6.0", "pystoi>=0.2.1"],
        "display": ["matplotlib>=2.2.3"],
        "doc": ["sphinx", "sphinx_rtd_theme", "numpydoc"],
    },
    packages=find_packages(include=["dave", "dave.debuggers", "dave.languages"]),
    package_data={'dave': ['assets/lldb_init.py', 'assets/.gdbinit', 'assets/.lldbinit']},
    include_package_data=True,
)
