#! /usr/bin/env python3

import os, sys, time, re

pid = os.getpid()               # get and remember parent pid

os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
output_file = "output_shell.txt"       # default output file

while True:
    user_input = input("$ ")         # request command and args from user
    if user_input == 'exit':       # exit shell if command is "exit"
        print("Thank you for using the shell.")
        break
    if user_input == "":
        continue

    inputFlag = False
    outputFlag = False
    pipeFlag = False

    # check if there's redirection or piping and get commands
    if ' < ' in user_input:
        new_args = user_input.split('<')
        inputFlag = True
    elif ' > ' in user_input:
        new_args = user_input.split('>')
        outputFlag = True
    elif ' | ' in user_input:
        new_args = user_input.split('|')
        pipeFlag = True
    else:
        new_args = user_input.split()

    print(new_args)
    cmd = new_args[0].strip() # command to run
            
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                     (os.getpid(), pid)).encode())
        if "/bin/" in cmd:
            cmd = cmd.replace("/bin/", "")
        if not inputFlag and not pipeFlag:
            args = [cmd, "shell.py"]
            os.close(1)                 # redirect child's stdout
            if outputFlag:
                output_file = new_args[1].strip()
            sys.stdout = open(output_file, "w")
            fd = sys.stdout.fileno() # os.open("output_shell.txt", os.O_CREAT)
            os.set_inheritable(fd, True)
            print("Command: ", cmd)
            print("hello world")
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                     (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                 childPidCode).encode())
