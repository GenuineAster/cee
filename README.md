cee
===

cee is a C++ evaluating IRC bot written in Python.

cee has greatly evolved as a project, and now supports many languages, such as:
- C++
 - GCC
 - Clang
 - Golf plugin
- Assembly:
 - NASM
 - TASM
 - GAS
- Lua
- Malbolge
- PHP
- Python
 - Python 2
 - Python 3
- JavaScript


cee requires:
- EasyProcess
- Kitchen
- sandbox

As of now, cee only functions on Linux and UNIX-like operating systems.

To run cee, simply type:
```bash
$ python2 run.py
```

configuring
==

cee's configuration files can be found in `config/`. You can add mutliple IRC servers, multiple IRC channels.

cee will not write its data to the configuration files, so any channels added prior to connection will be discarded upon exit.