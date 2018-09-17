#! /usr/bin/env python3

import os, sys, time, re

def run_command(user_input, output_file, scriptFlag):
    pid = os.getpid()               # get and remember parent pid
    os.write(1, ("About to fork (pid=%d)\n" % pid).encode())

    inputFlag = False
    outputFlag = False
    pipeFlag = False
    redirectFlag = True

    # check if there's redirection or piping and get commands
    if ' < ' in user_input:
        args = user_input.split('<')
        inputFlag = True
        if "runScript" not in args[0].strip():
            print("Invalid command.")
            return
    elif ' > ' in user_input:
        args = user_input.split('>')
        outputFlag = True
        output_file = args[len(args)-1].strip()   
        if ".txt" not in output_file:            # add .txt to files that don't have it
            output_file = output_file + ".txt"
        args[len(args)-1] = output_file        # update output file name from argument
    elif ' | ' in user_input:
        args = user_input.split('|')
        pipeFlag = True
        r, w = os.pipe()      # file descriptors r, w for reading and writing
    else:
        args = user_input.split()
        redirectFlag = False

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
        
        if not inputFlag and not pipeFlag:
            os.close(1)                 # redirect child's stdout
            if scriptFlag:
                sys.stdout = open(output_file, "a")
            else:
                sys.stdout = open(output_file, "w")
            fd = sys.stdout.fileno() # os.open("output_shell.txt", os.O_CREAT)
            os.set_inheritable(fd, True)
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, cmd)
                try:
                    if not redirectFlag:
                        os.execve(program, args, os.environ) # try to exec program
                    else:
                        os.execve(program, [args[0]], os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            os.write(2, ("Command not found.\n").encode())
            sys.exit(1)                 # terminate with error
            
        if inputFlag:
            with open(args[1].strip(), "r") as input_file:
                commands = input_file.readlines()
                commands = [x.strip() for x in commands]    # remove whitespace characters
                for command in commands:
                    run_command(user_input, output_file, True)
                    if command == '' or command == " " or command == "":
                        break

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
        run_command(user_input, output_file, False)
    
startShell()
