# `main`
## Added
- Added an editable colorbar to spectrogram view
- Added `magma` colormap for colorblind friendly spectrogram view
- Views colors adapt to the color theme
- A manual installation guide
## Changed
- User can no longer choose the color theme. It will stick to the system user theme
- No longer requires binary `Tk` libs to be installed on the system
- Switched to Pyside6 (Qt), no longer uses Tkinter/CustomTkinter
## Fixed
- A bug when a 2D entity previously out of scope would not appear
- A bug when trying to read uninitialized reference. These are now skipped
- A bug when trying to read a previous out of scope IIR entity
- Missing documentation for the Poles/Zeros view in the User's Guide

# v0.11.1
## Fixed
- Fixed `float_type` error in JUCE wrappers (mentionned in #18)
- Fixed crash when trying to read unitialized `old_svf_coeffs` in JUCE example

# v0.11.0
## Added
- All subcommands now supports flags. `dave show` with no variable will try and
display all possible variables in scope
## Changed
- Slightly improved drawing performances
## Fixed
- Fixed an internal crash when using `continue`/`next`
- Fixed possible hangout when closing the GUI

# v0.10.0
## Added
- Containers are now a specific type of audio Entity, this brings the possibility
to support other audio related structure in memory like filters
- Support for JUCE's IIR filters
## Changed
- Renamed `custom_containers` to `custom` to support any type of Entity
## Fixed
- Fixed a bug in dev mode : `dave` could not be loaded when installed in editable mode
- Fixed a bug where init lines would be duplicated in `~/.lldbinit` when reinstalling
- Fixed several small GUI bugs : render called twice, flickering UI, non consistent padding

# v0.9.3
## Fixed
- Debugger crash when using 2D nested containers
- Save to disc fails

# v0.9.2
## Fixed
- Fixed dave log output in Xcode
- Fixed formatter error in Xcode
- Fixed memory read error in Xcode
- UserWarning when in Waveform and Curve views

# v0.9.1
## Fixed
- `dave update` failing to update the `dave` cli script

# v0.9.0
## Added
- NaN and Inf values are detected and indicated on the plots
- NaN, Inf, num samples and num channels are indicated in the action frame
- Reimplementation of [Sudara's Sparklines](https://melatonin.dev/blog/audio-sparklines/)
## Changed
- Detect Tcl >= 9.0 in installation script and prevent from installing
## Fixed
- The installation script refused to install when having a custom_containers leftover

# v0.8.0
## Added
- Code documentation
- `dave inspect` command to help add support for new audio container class
- `dave help` command for a short help message in the debugger
## Changed
- Updated user guide
## Fixed
- 1D container support class were forced to use regex matching
- GDB logger was broken on the second process

# v0.7.0
## Added
- `choc` support
## Changed
- Improved audio views tab, matplotlib now reacts to window resize
- Fixed a minimum height for subfigures
- Views tab is now scrollable vertically
- Settings tab is now scrollable vertically
## Fixed
- Fixed an error when restarting dave on gdb
- Fixed an error with interleaved custom container example
- GDB was not tracking frame changes anymore

# v0.6.1
## Fixed
- gdb log formatting
- gdb hanging up when closing gdb after dave closing the dave gui


# v0.6.0
## Added
- The installation script has a dev mode to install davext from github
- Support for custom containers classes
## Changed
- Improved gdb frame change detection
- Improced gdb logging
## Fixed
- `freeze`, `concat`, `delete` command printing their argument on lldb
- `freeze`, `concat` commands not affecting the gui corresponding switches
- some debug prints when parsing a container

# v0.5.1
## Changed
- Channels count is now limited to 16, if above the view will not be plotted
## Fixed
- Python support
- `std::vector` bug with carray types
- `std/gsl::span` bug with const types
- GUI could not start cause of missing logo file


# v0.5.0
## Added
- Global settings section in `Settings`
- Global settings allow to switch between appearance mode
- Global settings allow to define default samplerate
- Samplerate field in container settings
## Changed
- container settings are now scrollable to allow the use of smaller window
## Fixed
- tooltip windows rendering on MacOS
- error when trying to restart the dave process
- both frozen and current data were labbeled frozen in spectrogram view

# v0.4.0
## Added
- Support for dark/light mode according to system settings
## Changed
- Dave now requires python >= 3.10
- Dave now uses [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
for better and more consistant UI across platforms
## Fixed
- grid placement issue when deleting a container
- Fixed [Issue #3](https://github.com/maxmarsc/dave/issues/3) by moving to CustomTkinter
- Fixed [Issue #5](https://github.com/maxmarsc/dave/issues/5) by manually starting
a new python interpreter

# v0.3.2
## Changed
- Improved error handling when starting the gui process
## Fixed
- Fixed #6 by adding "__1::" suffix in std typename matchers

# v0.3.1
## Changed
- `dave update` now update the dave script as well
## Fixed
- Fixed [issue #4](https://github.com/maxmarsc/dave/issues/4) by removing wrong
sys.path loading

# v0.3.0
## Added
- support for Microsoft's gsl::span
## Changed
## Fixed
- Fixed a parsing error on several c++ types
- Fixed #1 : template parser was ignoring characters after the last ">"

# v0.2.1
Firt version with changelog