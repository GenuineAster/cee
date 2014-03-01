/**

supervisor.c - A simple ptrace-based supervisor. Use at your own risk.

e.g.
sudo ./supervisor -u root -r / -w / -p profiles/default.profile /usr/bin/wget http://github.com
Resolving github.com... System call 49 was blocked.
Not allowed.

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

*/

#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <sys/stat.h>
#include <sys/param.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <sys/syscall.h>
#include <sys/user.h>
#include <sys/resource.h>
#include <string.h>
#include <stdbool.h>
 
#define PTRACE_O_TRACEFORK	 0x00000002
#define PTRACE_O_TRACEVFORK	0x00000004
#define PTRACE_O_TRACECLONE	0x00000008
#define PTRACE_O_TRACEEXEC	 0x00000010
#define PTRACE_O_TRACEVFORKDONE 0x00000020
#define PTRACE_O_TRACEEXIT	 0x00000040

#define PTRACE_O_MASK		 0x0000007f

#define PTRACE_EVENT_FORK	  1
#define PTRACE_EVENT_VFORK	 2
#define PTRACE_EVENT_CLONE	 3
#define PTRACE_EVENT_EXEC	  4
#define PTRACE_EVENT_VFORK_DONE 5
#define PTRACE_EVENT_EXIT	  6

#define SYSCALL_ALLOWED		1
#define SYSCALL_IGNORED		2

int pid = 0;

int timeLimit;
int memoryLimit;
int fileSizeLimit;
int fileCountLimit;

char* user;
char* chrootDir;
char* workingDir;

char* command;
char** commandArgs;

char* policyFile;

char syscalls[303];

void readCmdArgs(int argc, char** args) {
	int i = 1;

	char* option;
	char* value;

	timeLimit = 5;
	memoryLimit = 32;
	fileSizeLimit = 0;
	fileCountLimit = 10;

	user = NULL;
	chrootDir = NULL;
 
	policyFile = NULL;

	command = NULL;
	commandArgs = NULL;

	while (i <= argc - 2) {
		option = args[i];
		value = args[i + 1];
 
		if (strlen(option) != 2 || option[0] != '-') {
			break;
		}

		switch(option[1]) {
			case 'm':
				memoryLimit = atoi(value);
				break;
			case 't':
				timeLimit = atoi(value);
				break;
			case 'f':
				fileSizeLimit = atoi(value);
				break;
			case 'F':
				fileCountLimit = atoi(value);
				break;
			case 'r':
				chrootDir = value;
				break;
			case 'w':
				workingDir = value;
				break;
			case 'u':
				user = value;
				break;
			case 'p':
				policyFile = value;
				break;
			default:
				fputs("Unknown argument.\n", stderr);
				exit(1);
		}

		i += 2;
	}

	if (i == argc) {
		fputs("Command required.\n", stderr);
		exit(1);
	}

	if (user == NULL) {
		fputs("User required.\n", stderr);
		exit(1);
	}

	if (chrootDir == NULL) {
		fputs("Jail directory required.\n", stderr);
		exit(1);
	}

	if (workingDir == NULL) {
		fputs("Working directory required.\n", stderr);
		exit(1);
	}

	if (policyFile == NULL) {
		fputs("Policy file required.\n", stderr);
		exit(1);
	}

	command = args[i];
	commandArgs = args + i;
}

void readPolicyFile() {
	FILE *policy;

	char line[10];

	for (int j = 0; j < sizeof(syscalls); j++) {
		syscalls[j] = 0;
	}

	if ((policy = fopen(policyFile, "r")) == NULL) {
		fputs("Unable to open policy file.\n", stderr);
		fflush(stderr);
		exit(1);
	}

	while (fgets(line, sizeof(line), policy) != NULL)
	{
		if (strlen(line) < 3) {
			fputs("Invalid line in policy.\n", stderr);
			fflush(stderr);
			fclose(policy);
			exit(1);
		}

		switch (line[0]) {
			case 'a':
			case 'A':
				syscalls[atoi(&line[2])] = SYSCALL_ALLOWED;
				break;
			case 'i':
			case 'I':
				syscalls[atoi(&line[2])] = SYSCALL_IGNORED;
				break;
			default:
				fputs("Invalid instruction in policy.\n", stderr);
				fflush(stderr);
				fclose(policy);
				exit(1);
		}
	} 
	
	fclose(policy);  
}

void kill_and_exit(const char* msg) {
	if (pid != 0) {
		kill(pid, SIGKILL);
	}

	fputs(msg, stderr);
	exit(1);
}

void setResourceLimits() {
	struct rlimit rlim;

	rlim.rlim_cur = memoryLimit * 1024 * 1024;
	rlim.rlim_max = memoryLimit * 1024 * 1024;

	if (setrlimit(RLIMIT_AS, &rlim) != 0) {
		kill_and_exit("Unable to set resource limits.\n");
	}

	rlim.rlim_cur = timeLimit;
	rlim.rlim_max = timeLimit;

	if (setrlimit(RLIMIT_CPU, &rlim) != 0) {
		kill_and_exit("Unable to set resource limits.\n");
	}

	rlim.rlim_cur = fileSizeLimit;
	rlim.rlim_max = fileSizeLimit;

	if (setrlimit(RLIMIT_FSIZE, &rlim) != 0) {
		kill_and_exit("Unable to set resource limits.\n");
	}

	rlim.rlim_cur = fileCountLimit;
	rlim.rlim_max = fileCountLimit;

	if (setrlimit(RLIMIT_NOFILE, &rlim) != 0) {
		kill_and_exit("Unable to set resource limits.\n");
	}
}

void handle_syscall(int pid) {
	bool handled = false;

	struct user_regs_struct regs;

	if (ptrace(PTRACE_GETREGS, pid, NULL, &regs) != 0) { 
		kill_and_exit("Unable to read application registers.\n");
	}

	unsigned long int syscall = regs.orig_rax;

	if (syscall >= 0 && syscall < sizeof(syscalls)) {
		switch (syscalls[syscall]) {
			case SYSCALL_ALLOWED:
				if (ptrace(PTRACE_SYSCALL, pid, 0, 0) != 0) {
					kill_and_exit("Unable to continue exection after an allowed system call.\n");
				}
	
				handled = true;
	
				break;
			case SYSCALL_IGNORED:
				regs.rax = 0;
				regs.orig_rax = SYS_getpid;
	
				if (ptrace(PTRACE_SETREGS, pid, NULL, &regs) != 0) {
					kill_and_exit("Unable to modify application registers.\n");
				}
	
				if (ptrace(PTRACE_SYSCALL, pid, 0, 0) != 0) {
					kill_and_exit("Unable to continue execution after an ignored system call.\n");
				}
	
				handled = true;
	
				break;
			default:
#ifdef DEBUG
				printf("System call %ld was blocked.\n", syscall);
#endif
				break;
		}
	} else {
#ifdef DEBUG
		printf("Unknown syscall %ld.\n", syscall);
#endif
	}


	if (!handled) {
		if (ptrace(PTRACE_KILL, pid, 0, 0) != 0) {
			kill_and_exit("Unable to kill the process.\n");
		}

		kill_and_exit("Not allowed.\n");
	}
}

int main(int argc, char** args) { 
	readCmdArgs(argc, args);

	readPolicyFile();

	if ((pid = fork()) == 0) {
		// Child process

		if (ptrace(PTRACE_TRACEME, 0, 0, 0) != 0) {
			kill_and_exit("Unable to trace execution.\n");
		}

		setResourceLimits();

		struct passwd* pwd = getpwnam(user);

		if (pwd == NULL)
		{
			kill_and_exit("Unable to lookup user.\n");
		}	 

		if (chroot(chrootDir) != 0) {
			kill_and_exit("Chroot failed.\n");
		}	

		if (chdir(workingDir) != 0) {
			kill_and_exit("Chdir failed.\n");
		}

		if (setuid(pwd -> pw_uid) != 0) {
			kill_and_exit("Unable to change user.\n");
		}

		char* environ[] = { NULL };

		if (execve(command, commandArgs, environ) != 0) {
			kill_and_exit("Exec failed.\n");
		}
	} else {
		int status;

		// Wait for execve
		wait(&status);

		if (ptrace(PTRACE_SYSCALL, pid, 0, 0) != 0) {
			kill_and_exit("Unable to continue execution after exec.\n");
		}

		while(1) { 
			wait(&status);

			if (WIFEXITED(status)) {
				break;
			}

			handle_syscall(pid); 
		}
	}

	return 0; 
} 

