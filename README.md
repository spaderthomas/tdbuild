# Installattion

`pip install tdbuild`

# Usage

Usage is dead simple. Use `tdbuild new` to create a Python script called `tdfile.py`. Hand-edit some basic inputs to the compiler (what are your source files? what is the executable called? etc). Then, run `tdbuild` to build and `tdbuild run` to run your code. Altogether, it looks like this:

 ```
 mkdir new_project && cd new_project
 
 tdbuild new
 
 emacs tdfile.py
 
 tdbuild
 
 tdbuild run
 ```
# Why did you write this software?
Do you find CMake's scripting language arcane and its documentation unusable?

Do you struggle to install and maintain a usable set of Unix tools on Windows? And do you hate creating Makefiles that are cross platform?

Do you want to write code instead of learning how to use a flashy new build system like Meson?

Yeah. Me too. Use this C/C++ build system. Fundamentally, all it does it build a command line for your compiler. It's that simple. If `tdbuild` ever becomes insufficient for you, you can copy thee command line and do whatever the hell you want with it. You can also add custom flags to the command line.

Yes, this means your whole program will rebuild every time. If your program is very big or uses a lot of templates, your build times will be slow. If you are the target audience for this build tool, then you won't care. `tdbuild` is not for enterprise software, nor is it for large open source projects. It's for people who just want to write a damn C/C++ project that compiles on all platforms without screwing with build tools for a few days.

Some projects that I build with `tdbuild` every day:
- https://github.com/spaderthomas/tdengine, my game engine.
- https://github.com/spaderthomas/tdeditor, my text editor.

