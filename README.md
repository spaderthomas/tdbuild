# Installation

`pip install tdbuild`

# Usage

Usage is dead simple. Use `tdbuild new` to create a Python script called `tdfile.py`. Hand-edit some basic inputs to the compiler (what are your source files? what is the executable called? etc). Then, run `tdbuild` to build and `tdbuild run` to run your code. Altogether, it looks like this:

 ```
 mkdir new_project && cd new_project
 
 python -m tdbuild new
 
 emacs tdfile.py
 
 python -m tdbuild
 
 python -m tdbuild run
 ```
# Why did you write this software?
Do you find CMake's scripting language arcane and its documentation unusable?

Do you struggle to install and maintain a usable set of Unix tools on Windows? And do you hate creating Makefiles that are cross platform?

Do you want to write code instead of learning how to use a flashy new build system like Meson?

Yeah. Me too. Use this C/C++ build system. Fundamentally, all it does it build a command line for your compiler. It's that simple. If `tdbuild` ever becomes insufficient for you, you can copy the command line and do whatever the hell you want with it. You can also add custom flags to the command line.

Yes, this means your whole program will rebuild every time. If your program is very big or uses a lot of templates, your build times will be slow. If you are the target audience for this build tool, then you won't care. `tdbuild` is not for enterprise software, nor is it for large open source projects. It's for people who just want to write a god damn C/C++ project that compiles on all platforms without screwing with build tools for a few days.

Some projects that I build with `tdbuild` every day:
- https://github.com/spaderthomas/tdengine, my game engine.
- https://github.com/spaderthomas/tdeditor, my text editor.

# Options

Your build options are simply a Python dictionary. That's it. Here's a list of all the possible options the tool supports:

### Top Level
`options.project`:

`options.source_dir`:

`options.include_dirs`:

`options.lib_dir`:

`options.build_dir`:

`options.source_files`:

`options.build_type`:

`options.binary_type`:

`options.cpp`:

`options.cpp_standard`:

`options.disable_console`:

`options.defines`:


### Windows
`options.Windows.system_libs`:

`options.Windows.user_libs`:

`options.Windows.dlls`:

`options.Windows.ignore`:

`options.Windows.arch`:

`options.Windows.out`:

`options.Windows.runtime_library`:

`options.Windows.warnings`:

`options.Windows.extras`:


## Linux
`options.Linux.compiler`:

`options.Linux.user_libs`:

`options.Linux.system_libs`:

`options.Linux.extras`:

`options.Linux.out`:
