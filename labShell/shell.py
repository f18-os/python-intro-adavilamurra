#! /usr/bin/env python3

import os, sys, time, re

def run_command(user_input, output_file, scriptFlag):
    pid = os.getpid()               # get and remember parent pid
    os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
    
    inputFlag = False
    outputFlag = False
    pipeFlag = False

    # check if there's redirection or piping and get commands
    if ' | ' in user_input:
        args = user_input.split(' | ')
        pipeFlag = True
        r, w = os.pipe()      # file descriptors r, w for reading and writing
    elif ' > ' in user_input:
        args = user_input.split(' > ')
        outputFlag = True
        output_file = args[len(args)-1].strip()   
        if ".txt" not in output_file:            # add .txt to files that don't have it
            output_file = output_file + ".txt"
        args = args[0].split()
    elif ' < ' in user_input:
        args = user_input.split(' < ')
        inputFlag = True
        input_name = args[len(args)-1].strip()
    else:
        args = user_input.split()

    cmd = args[0].strip()      # command to run
    print(args)
    
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                     (os.getpid(), pid)).encode())
        if "/bin/" in cmd:
            cmd = cmd.replace("/bin/", "")
        
        if not pipeFlag:
            if outputFlag:
                os.close(1)                 # redirect child's stdout
                sys.stdout = open(output_file, "w")
                fd = sys.stdout.fileno() # os.open("output_shell.txt", os.O_CREAT)
                os.set_inheritable(fd, True)
                os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, cmd)
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            os.write(2, ("Command not found.\n").encode())
            sys.exit(1)                 # terminate with error       

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                     (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                     childPidCode).encode())

def startShell():
    output_file = "output_shell.txt"       # default output file
    os.write(1, ("Welcome to the shell.\n").encode())
    while True:
        user_input = input("$ ")         # request command and args from user
        if user_input == 'exit':       # exit shell if command is "exit"
            os.write(1, ("Thank you for using the shell.\n").encode())
            break
        if user_input == "":
            continue
        args = user_input.split()
        if args[0] == "cd":
            if len(args) < 2:
                continue
            if args[1] == "..":
                currentDir = os.getcwd()
                newDir = currentDir.rsplit('/', 1)[0]
                os.chdir(newDir)
                continue
            else:
                os.chdir(args[1])
                continue
        run_command(user_input, output_file, False)
    
startShell()
