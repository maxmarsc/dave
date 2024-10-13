# DAVE user guide
This is the user guide for DAVE

## DAVE setup
When adding DAVE to your system it's important to understand it's composed of
two parts : the `dave` python module itself, and the bindings for the debuggers.

The bindings for gdb and lldb uses the `~/.gdbinit` and `~/.lldbinit` files
to automatically load the dave module at runtime. If the module is not accessible
then you will be inform.

### The `dave` command line tool
After installation (and reloading your .bashrc/.zshrc file), you should have access to
the `dave` command line tool :

```
usage: dave [-h] {status,bind,unbind,update, uninstall} [{lldb,gdb,both}]

Helper script to manage DAVE

subcommands:
        dave status
                        Print information about the current dave installation
        dave bind [{lldb, gdb, both}]
                        Bind the selected debuggers to dave
                        Default to 'both' on Linux and 'lldb' on MacOS

        dave unbind [{lldb, gdb, both}]
                        Unbind the selected debuggers from dave
                        Default to 'both' on Linux and 'lldb' on MacOS

        dave update
                        Update the dave package and the bindings

        dave uninstall 
                        Uninstall dave completely

options:
        -h, --help      show this help message and exit
```

## Debugger commands
DAVE adds a set of new commands to your debugger

### `dave show`
`dave show` is the most basic command of DAVE

The usage is :
```
dave show VARIABLE [DIM1[,DIM2]]
```

You'd use it as using `print` or `display` in gdb/lldb, by giving it a variable
that it used in your program to hold/contains/points to audio data (mono or multichannel).

On the first call it will open up the GUI window to show the audio content of the
variable. Then, on each breakpoint/step/frame change, DAVE will check if the variable
is in scope, and if so, updates its data and plot it again.

After each call, `dave show` will print out the id for this container, to use
in case of naming conflicts.

*Important notice* : `show` does not behave exactly like `display`. To check if a 
variable "is in scope", `display` only checks if a variable has the same name in 
the current scope.  
DAVE on the other hand checks both the name **and the address** 
of a variable.

#### Optionnal arguments : `[DIM1[,DIM2]]`
Some types does not provide dimensions of the audio content, like C pointers.
In such case the caller must provide the dimensions of the audio content. Only `DIM1`
for a simple pointer (eg: `float*`), both `DIM1,DIM2` for a nested pointer (eg: `float**`)

### `dave delete`
The usage is :
```
dave delete VARIABLE|CONTAINER_ID
```

This command tells dave to stop tracking an audio container. If you delete the
last container tracked, then the GUI automatically stops.

You can give this command either (unique) id of a tracked container, or a variable
name. In case of naming conflicts, this first container added with this name will
be deleted.

### `dave freeze`
The usage is :
```
dave freeze VARIABLE|CONTAINER_ID
```

This command enable/disable the *Freeze* setting for the given audio container. See
Actions for details.

You can give this command either (unique) id of a tracked container, or a variable
name. In case of naming conflicts, this first container added with this name will
be deleted.

### `dave concat`
The usage is :
```
dave concat VARIABLE|CONTAINER_ID
```

This command enable/disable the *Concatenate* setting for the given audio container.
See Actions for details.

You can give this command either (unique) id of a tracked container, or a variable
name. In case of naming conflicts, this first container added with this name will
be deleted.


## Data update settings
This settings affect how an update of containers's data affect the rendering.

### Freeze
When enabling "freeze" on a container, the current data (at the time of the 
change of setting) of this container is kept in memory to be plotted at each update
alongside the new data

Depending on the view type, it behaves differently :
- If the view type support multiple plots on the same figure (Waveform, Curve ...),
both frozen and new data are plot on the same figure
- If the view type does not supports multiple plots on the same figure (Spectrogram)
then a subfigure is created for the frozen data

When disabling the frozen setting, the frozen data is deleted.

### Concatenate
When enabling "concat" on a container, nothing happens yet. When new data comes in,
it is concatenated, channel-wise, to the old data, left-to-right

When disabling the "concat" setting, the old data is deleted.

## GUI window
DAVE uses a GUI to show you audio content from your debugger. The GUI consists
of a single window, with two tabs : the `Views` and the `Settings`

### Validating inputs
Some settings will require you to enter manually the value you'd like for the settings. When doing so you can apply the changes by pressing `<Enter>`. If the value is not valid for the settings, it will give you an error message in the console and revert back to the last value.

### The `Views` tab
![Views](.pictures/views.png)

On `1.` are the audio views of your audio data. One plot for each channel, for
each container currently in scope.

On `2.` are the actions buttons :
 - `F` enable/disable the *Freeze* setting of the container
 - `C` enable/disable the *Concatenate* setting of the container
 - `S` "Save to disc" : opens up a window to save the current shown data to disc (supported format are `.npy` files and WAV signed integers, depending on the data)

On `3.` are the matplotlib controls. These allow you to navigate and zoom within
the plots. The save button saves the figures, and not the data.

### The `Settings` tab
![Settings](.pictures/settings.png)

On this tab you have a setting menu for each container currently in scope.

#### Data layout
On `1.` you have the *Data Layout* selection. The type of layout are :
- real 1D : monophonic pcm samples
- real 2D : multichannel pcm samples
- complex 1D : monophonic complex values
- complex 2D : multichannel complex values

When using a 1D container (eg: `std::vector<float>`), you can uses this section 
to tell dave you actually uses this container to store 2D data.

When using both 1D or 2D container, you can also indicate you use the container
to store real/complex data. As in C/C++ real and complex floating point values
can be aliased. **Forcing a complex layout on real data requires an even number of samples**

A data layout dictates what views are available, so when changing the layout, the
available views might changes as well.

#### Channel section
**This section only shows up when the container uses a 2D layout**

On `2.` you have the channel section. If your container is 2D then it will show
you how many channels it as. If it's 1D but you forced a 2D layout, you can 
type how many channels it has.

When using a 2D layout on a 1D container, you can also indicates that the samples
of each channel are interleaved by clicking on the `interleaved` button. DAVE 
will then de-interleave the samples for rendering.

When using a container with 2 channels, you can decide to use mid/side rendering,
by clicking on the `mid/side` button.

#### View section
On `3.` you have the view section. You can use the selector to select which view 
(see possibles views) to use to render your audio data.

Some views (PSD, Spectrogram) have additional settings which you can change in 
this section.

#### General section
On `4.` you have the general section, where option are the same for every container.

It contains the delete button (X), which marks the container for deletion 
(like `dave delete`). TODO: It should also contains the samplerate setting.


## Possibles views
### Waveform
Available on **real** (1D/2D) data layout.

![Waveform](.pictures/waveform.png)

The waveform view is the default and most basic audio view. It plots the audio
samples, and centers vertically the plots on zero.


### Curve
Available on **real** (1D/2D) data layout.

![Curve](.pictures/curve.png)

The curve view is like the waveform view, excepts it does not centers vertically
the graph on zero.

Available settings :
- X scale : `linear` or `log`
- Y scale : `linear` or `log`

### PSD
Available on **real** (1D/2D) data layout.

![PSD](.pictures/psd.png)

The PSD view computes and plot the power spectral density of the signal. It uses
[matplotlib's PSD implementation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.psd.html)

Available settings :
- nfft : `[16: 4096]` default to `256`
- overlap : `[0.01: 0.99]` default to `0.5`
- window type : `hanning`, `blackman` or `none`

### Spectrogram
Available on **real** (1D/2D) data layout.

![Spectrogram](.pictures/spectrogram.png)

The Spectrogram view computes and plot the spectrogram of the signal. It uses
[matplotlib's specgram implementation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.specgram.html)

Available settings :
- nfft : `[16: 4096]` default to `256`
- overlap : `[0.01: 0.99]` default to `0.5`
- window type : `hanning`, `blackman` or `none`

**Note :** If for some reason the computation of the spectrogram is not possible
(ex: divide by zero), the concerned channel will be left blanked like in the pictures.

### Magnitude view
Available on **complex** (1D/2D) data layout.

![Magnitude](.pictures/magnitude.png)

The magnitude view computes and plot the magnitude of a complex signal.

### Magnitude view
Available on **complex** (1D/2D) data layout.

![Phase](.pictures/phase.png)

The phase view computes and plot the phase of a complex signal.

## Supported containers
For now DAVE support samples as `float`, `double`, `std::complex` and C's `complex`

Supported audio containers are :

__1D (mono) containers__:
- `std::array`
- `std::vector`
- `std::span`
- [Microsoft's `gsl::span`](https://github.com/microsoft/GSL/blob/main/include/gsl/span) 
- `C array`
- `pointer`

__2D (multichannel) containers__:
- Any nesting of 1D containers
- `juce::AudioBuffer`
- `juce::dsp::AudioBlock`

Currently supported OS are Linux and MacOS. Both GNU and LLVM stdlib
implementation are supported.