supervisor
==========

A simple ptrace-based supervisor. Use at your own risk.

- Run a process as another user in a chroot jail
- Enforce memory, CPU time and file handle limits
- Define syscall policies in multiple profiles

Usage
=====

    supervisor <options> command args
    
    Options:
    
    -m limit    - Set the memory limit in mb
    -t limit    - Set the time limit in seconds
    -f limit    - Set the file size limit in bytes
    -F limit    - Set the file count limit
    -r dir      - Set the chroot jail directory; required
    -w dir      - Set the working directory; required
    -u user     - Set the name of the executing user; required
    -p file     - Set the policy file; required

Example
=======

In debug mode (make debug):

    sudo ./supervisor -u root -r / -w / -p profiles/default.profile /usr/bin/wget http://github.com
    Resolving github.com... System call 49 was blocked.
    Not allowed.

System call 49 (bind) was blocked by the default profile.

Profiles
========

Profiles are simple text files containing simple instructions.

Each line contains with a letter and a system call ID. A line beginnning with the letter `a` defines an allowed system call. A line beginning with the letter `i` defines an ignored system call. An attempt to call any other system call terminates execution of the supervised executable. Ignored system calls are skipped.

License
=======

    Copyright (c) 2012 Phil Freeman
    All rights reserved.
    
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in the
          documentation and/or other materials provided with the distribution.
        * Neither the name of the <organization> nor the
          names of its contributors may be used to endorse or promote products
          derived from this software without specific prior written permission.
    
    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
