from setuptools import setup, find_packages

VERSION = "0.13.0"

with open("README.md", encoding="utf-8") as fh:
    pypi_header = """
<p align="center"><b>Base python module for the DAVE project</b></p>

**Important:** It is not recommended to install DAVE directly from pypi, you
should rather use the install script as show in the "Project Setup" section.

"""
    long_description = pypi_header + fh.read()
    long_description = long_description.replace(
        ".pictures/",
        f"https://media.githubusercontent.com/media/maxmarsc/dave/v{VERSION}/.pictures/",
    )

setup(
    name="davext",
    version=VERSION,
    author="maxmarsc",
    python_requires=">3.10.1",
    author_email="maxime.coutant@protonmail.com",
    url="https://github.com/maxmarsc/dave",
    description="base module for the DAVE debugger extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "PySide6==6.9.0",
        "scipy==1.15.2",
        "pyqtgraph==0.13.7",
        "darkdetect==0.8.0",
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
            "assets/dave_logo_v6.png",
        ],
        ":": ["LICENSE"],
    },
    include_package_data=True,
)
