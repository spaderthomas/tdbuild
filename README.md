Do you find CMake's scripting language arcane and its documentation unusable?

Do you struggle to install and maintain a usable set of Unix tools on Windows? And do you hate creating Makefiles that are cross platform?

Do you want to write code instead of learning how to use a flashy new build system like Meson?

Yeah. Me too. Use this C/C++ build system. It's dead simple: Run `tdbuild new` to create a new project. This makes a `tdfile` with two things:

1. A dictionary of what your program has, in plain language

2. A simple class with simple hooks for prebuild, build, run, and install.

After filling this out, running `tdbuild` will build your program and running `tdbuild run` will run it. It's that simple. If `tdbuild` ever becomes insufficient for you, you can manually add extra flags with tdbuild, or just copy the command line and do whatever the hell you want with it.

Yes, this means your whole program will rebuild every time. If your program is very big or uses a lot of templates, your build times will be slow. If you are the target audience for this build tool, then you won't care. `tdbuild` is not for enterprise software, nor is it for large open source projects. It's for people who just want to write a damn C/C++ project that compiles on all platforms without screwing with build tools for a few days.

Some projects that I build with `tdbuild` every day:
- https://github.com/spaderthomas/tdengine, my game engine.
- https://github.com/spaderthomas/tdeditor, my text editor.

