# `main`
## Added
## Changed
- Channels count is now limited to 16, if above the view will not be plotted
## Fixed
- Python support

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