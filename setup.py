from setuptools import setup, find_packages

VERSION = "0.3.1"

with open("README.md", encoding="utf-8") as fh:
    pypi_header = """
<p align="center"><b>Base python module for the DAVE project</b></p>

**Important:** It is not recommended to install DAVE directly from pypi, you
should rather use the install script as show in the "Project Setup" section.

"""
    long_description = pypi_header + fh.read()
    long_description.replace(
        'src=".pictures/phase.png"',
        f'src="https://github.com/maxmarsc/dave/raw/refs/tags/v{VERSION}/.pictures/phase.png"',
    )

setup(
    name="davext",
    version=VERSION,
    author="maxmarsc",
    author_email="maxime.coutant@protonmail.com",
    url="https://github.com/maxmarsc/dave",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "matplotlib>=3.9.2",
    ],
    license="GPLV3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Debuggers",
    ],
    packages=find_packages(),
    package_data={
        "dave": [
            "assets/lldb_init.py",
            "assets/.gdbinit",
            "assets/.lldbinit",
            "assets/dave",
        ],
        ":": ["LICENSE"],
    },
    include_package_data=True,
)
