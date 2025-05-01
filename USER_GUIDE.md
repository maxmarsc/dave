# DAVE user guide
This is the user guide for DAVE. It's supposed to be the official documentation
for DAVE. If you think something is not clear or missing, please open an issue.

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

## Debugger formatting
DAVE provides custom formatters for many audio containers, for both LLDB and GDB. They
look like this :

*Example:* `juce::dsp::AudioBlock<float>`
```
2 channels 256 samples, min -9.9998E-01, max 1.0000E+00 {
  dSparkline[0] = "[0⎻⎺‾⎺⎻x⎼_⎽⎼x⎺‾⎺⎻x⎽_⎽—x⎺‾⎺⎻x⎽_⎽⎼x⎺‾⎺⎻x⎽_⎽—x⎺‾⎺⎻x⎽_⎼x⎺‾⎺—x_⎽—x⎺‾⎺⎻x⎽_⎽⎼x⎺‾⎺⎻x⎽_⎽—x⎺‾⎺—x_⎼x⎺‾⎺⎻x⎽_⎽⎼x⎺‾⎺x⎽_⎽⎼x⎺‾⎺—x_⎽⎼x⎺‾⎻x⎽_⎽—x‾⎺⎻x⎽_⎼x⎺‾⎺—x_⎽—x‾⎺⎻x_⎽⎼x‾⎺⎻x_⎽⎼x‾⎺⎻x_⎽—x‾⎺—x_]"
  dSparkline[1] = "[0⎻⎺‾⎺⎻x⎼_⎽⎼x⎺‾⎺⎻x⎽_⎽—x⎺‾⎺⎻x⎽_⎽⎼x⎺‾⎺⎻x⎽_⎽—x⎺‾⎺⎻x⎽_⎼x⎺‾⎺—x_⎽—x⎺‾⎺⎻x⎽_⎽⎼x⎺‾⎺⎻x⎽_⎽—x⎺‾⎺—x_⎼x⎺‾⎺⎻x⎽_⎽⎼x⎺‾⎺x⎽_⎽⎼x⎺‾⎺—x_⎽⎼x⎺‾⎻x⎽_⎽—x‾⎺⎻x⎽_⎼x⎺‾⎺—x_⎽—x‾⎺⎻x_⎽⎼x‾⎺⎻x_⎽⎼x‾⎺⎻x_⎽—x‾⎺—x_]"
  [...]
}
```

They always provide :
1. A summary with channels, samples, min and max values (only for scalar)
2. A *sparkline* for each channel : *data-intense, design-simple, word-sized graphics*
3. The member variables of the container

This implementation is a replication of [Sudara's Sparklines](https://melatonin.dev/blog/audio-sparklines/) but
for more containers, debuggers and frameworks.

### Sparklines
A sparkline is a **normalized** 3-bit decimated version of a waveform. It can contains the following chars :
- 0 is a true 0
- 0(234) shows a chunk of zeros, in this case 234
- x represents a zero crossing
- E is out of bounds (below -1.0, above 1.0)
- I = Inf (Infinity, meaning you've divided by zero)
- N = NaN (undefined calculation that's not INF)

If the container are interleaved, the samples will be deinterleaved. 

Samples are not downsampled, which means you have **a char for each sample** in 
the channel. If you have a big block size, your debugger/IDE will likely truncate
the ascii plot. If you need full resolution, consider using the GUI.

### Supported entities
Since the formatters will override any other formatter you might have, DAVE formatters
are disabled for the the standard library (C, C++).


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

On the first call it will open up the GUI window to plot the content of the
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

This command tells dave to stop tracking an audio entity. If you delete the
last container tracked, then the GUI automatically stops.

You can give this command either (unique) id of a tracked entity, or a variable
name. In case of naming conflicts, this first entity added with this name will
be deleted.

### `dave freeze`
The usage is :
```
dave freeze VARIABLE|CONTAINER_ID
```

This command enable/disable the *Freeze* setting for the given audio entity. See
Actions for details.

You can give this command either (unique) id of a tracked entity, or a variable
name. In case of naming conflicts, this first entity added with this name will
be deleted.

### `dave concat`
The usage is :
```
dave concat VARIABLE|CONTAINER_ID
```

This command enable/disable the *Concatenate* setting for the given audio entity.
See Actions for details.

You can give this command either (unique) id of a tracked entity, or a variable
name. In case of naming conflicts, this first entity added with this name will
be deleted.


### `dave inspect`
The usage is :
```
dave inspect VARIABLE
```

This is useful when you want to add support for a new type of audio entity, it
will print out the type as deduced by your debugger.

It should resolve automatically typedefs and alias. If not please raise an issue.

### `dave help`
The usage is :
```
dave help
```
Display a short help message which redirects to this page

## Data update settings
This settings affect how an update of entity's data affect the rendering.

### Freeze
When enabling "freeze" on a entity, the current data (at the time of the 
change of setting) of this entity is kept in memory to be plotted at each update
alongside the new data

Depending on the view type, it behaves differently :
- If the view type support multiple plots on the same figure (Waveform, Curve ...),
both frozen and new data are plot on the same figure
- If the view type does not supports multiple plots on the same figure (Spectrogram)
then a subfigure is created for the frozen data

When disabling the frozen setting, the frozen data is deleted.

### Concatenate
*Not all type of entities are compatible with the concatenate feature*
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
each entity currently in scope.

On `2.` are the actions switches/buttons :
 - `Freeze` enable/disable the *Freeze* setting of the entity
 - `Concat` enable/disable the *Concatenate* setting of the entity
 - `Save` : opens up a window to save the current shown data to disc (supported format are `.npy` files and WAV signed integers, depending on the data)

On `3.` are the matplotlib controls. These allow you to navigate and zoom within
the plots. The save button saves the figures, and not the data.

### The `Settings` tab
![Settings](.pictures/settings.png)

The settings tab contains global settings and settings for each entity currently
in scope.

In several places you'll be able to edit values, either from a text entry or a 
drop-down list. When editing through a text entry, your input will only be validated
and used after pressing the `<Enter>` key.

#### Global settings
![Global settings](.pictures/settings_global.png)

From left-to-right :
- Appearance settings : select from dark, light or system
- Default samplerate : the default samplerate to use for each container

#### Entity settings
![Entity settings](.pictures/settings_container.png)

For each entity in scope you can see a frame with settings for this entity.

From left-to-right :

##### `Container` Data layout selection
The type of layout are :
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

##### Channel section
First the number of channels of the entity. Editable if the container is 1D
but you forced a 2D layout.

###### `Container` channel section 
Then the interleaved switch. Editable if the container is 1D
but you forced a 2D layout. Some containers might be interleaved by nature, this
will reflect it.
This will change how dave interpret each channel.

Then the mid/side switch. Editable if the container contains 2 channels. If selected
then dave will not render the channels but the mid/side channels.

##### View section
You can use the selector to select which view 
(see possibles views) to use to visualize your audio data.

Some views (PSD, Spectrogram) have additional settings which you can edit in 
this section.

##### General section
Finally the general section. From left-to-right it contains:
- the samplerate setting
- the delete button (X) to tell dave to stop track this entity

## Possibles views
### Container: Waveform
Available on **real** (1D/2D) data layout.

![Waveform](.pictures/waveform.png)

The waveform view is the default and most basic audio view. It plots the audio
samples, and centers vertically the plots on zero.


### Container: Curve
Available on **real** (1D/2D) data layout.

![Curve](.pictures/curve.png)

The curve view is like the waveform view, excepts it does not centers vertically
the graph on zero.

Available settings :
- X scale : `linear` or `log`
- Y scale : `linear` or `log`

### Container: PSD
Available on **real** (1D/2D) data layout.

![PSD](.pictures/psd.png)

The PSD view computes and plot the power spectral density of the signal. It uses
[matplotlib's PSD implementation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.psd.html)

Available settings :
- nfft : `[16: 4096]` default to `256`
- overlap : `[0.01: 0.99]` default to `0.5`
- window type : `hanning`, `blackman` or `none`

### Container: Spectrogram
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

### Container: Magnitude view
Available on **complex** (1D/2D) data layout.

![Magnitude](.pictures/magnitude.png)

The magnitude view computes and plot the magnitude of a complex signal.

### Container: Phase view
Available on **complex** (1D/2D) data layout.

![Phase](.pictures/phase.png)

The phase view computes and plot the phase of a complex signal.

### IIR Filter: Magnitude view

![IIR Magnitude](.pictures/iir_magnitude.png)

The magnitude view plot the magnitude/frequency response of the filter

### IIR Filter: Phase view

![IIR Phase](.pictures/iir_phase.png)

The magnitude view plot the magnitude/frequency response of the filter

## Supported Entities
For now DAVE support samples as `float`, `double`, `std::complex` and C's `complex`

Currently supported audio containers are :

__1D (mono) containers__:
- `std::array`
- `std::vector`
- `std::span`
- [Microsoft's `gsl::span`](https://github.com/microsoft/GSL/blob/main/include/gsl/span) 
- `C array`
- `pointer`
- `choc::buffer::MonoView`
- `choc::buffer::MonoVBuffer`


__2D (multichannel) containers__:
- Any nesting of C/C++ standards 1D containers
- `juce::AudioBuffer`
- `juce::dsp::AudioBlock`
- `choc::buffer::InterleavedView`
- `choc::buffer::InterleavedBuffer`
- `choc::buffer::ChannelArrayView`
- `choc::buffer::ChannelArrayBuffer`

Currently supported IIR filter/coefficients are :
- `juce::dsp::IIR::Filter`
- `juce::dsp::IIR:Coefficients`

Currently supported OS are Linux and MacOS. Both GNU and LLVM stdlib
implementation are supported.

### Custom entities
You can add support for custom containers using a bit of python scripting.

To proceed you need to:
1. Use the `dave inspect` debugger command to identify the name of the types you want to support
2. Create a `~/.dave/custom` folder. It should contains all your custom code
3. Add a new `Entity` python subclass for each entity you want to support (see below)
4. Register the container class using `EntityFactory().register()`
5. Import your container in the `~/.dave/custom/__init__.py` file 

#### Examples
Some examples are provided :
- The [examples/custom_containers.cpp](examples/custom_containers.cpp) file contains some custom classes to add support to
- The [examples/custom]([examples/custom) folder contains the python code to support these class

To test these examples, just copy (or symlink) the `examples/custom` in
the `.dave` folder.

#### The `Entity` class
DAVE uses the abstract [`Entity`](dave/server/entity.py) class as an abstraction layer to support all
types of audio entities.

To add support for your own classes, you should inherit from `Entity`. However, unless
you wanna add support for a completely new type of Entity, you should inherits from
one of the following classes :

- [`Container1D`, `Container2D`](dave/server/container.py) to add support for a 
new type of audio container
- [`IIR`](dave/server/iir.py) to add support for a new type of IIR filter


Find examples on how to inherit from these in the [languages folder](dave/server/languages/). 
To identify the actual typename of your classes as seen by DAVE you can use the `dave inspect` command