#! /usr/bin/env python3

import os, sys, time, re, fileinput

def run_execve(args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        program = "%s/%s" % (dir, args[0].strip())
        try:
            os.execve(program, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly 

def run_command(user_input):
    pid = os.getpid()               # get and remember parent pid
    
    inputFlag = outputFlag = pipeFlag = False

    # check if there's redirection or piping and get commands
    if ' | ' in user_input:
        processes = user_input.split(' | ')
        args = processes[0].split()
        pipeFlag = True
        pr, pw = os.pipe()      # file descriptors r, w for reading and writing
        for f in (pr, pw):
            os.set_inheritable(f, True)
        print("pipe fds: pr=%d, pw=%d" % (pr,pw))
        
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
        args[len(args)-1] = args[len(args)-1].strip()

    else:
        args = user_input.split()

    rc = os.fork()    # begin forking

    if rc < 0:      #fork failed
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:      # child
        if "/bin/" in args[0]:
            args[0] = args[0].replace("/bin/", "")
            
        if outputFlag:
            os.close(1)                 # redirect child's stdout
            sys.stdout = open(output_file, "w")
            os.set_inheritable(1, True)

        if inputFlag:
            os.close(0)
            sys.stdin = open(args[len(args)-1], "r")
            os.set_inheritable(0, True)
            args = [args[0]]
            
        if pipeFlag:
            os.close(1)
            os.dup(pw)
            os.set_inheritable(1, True)
            for fd in (pr, pw):
                os.close(fd)

        run_execve(args)
        os.write(2, ("Command not found.\n").encode())
        sys.exit(1)                 # terminate with error 1

    else:            # parent (forked ok)
        if not pipeFlag:
            childPidCode = os.wait()
        else:
            os.close(0)
            os.dup(pr)
            os.set_inheritable(0, True)
            for fd in (pw, pr):
                os.close(fd)
            run_execve(processes[1].split())
            
def startShell(user_input, e):
    while True:
        if user_input == "" or user_input == " " or "cd" in user_input:
            user_input = input(e["PS1"])         # request command and args from user
            if "cd" not in user_input:
                continue
        if "\n" in user_input or "\\n" in user_input:
            #os.write(1, ("user input: %s \n" % user_input).encode())
            for command in user_input.split("\\n"):
                #os.write(1, ("command: %s \n" % command).encode())
                if len(command) > 3:
                    run_command(command.strip())
            user_input = ""
            continue
        if user_input == "exit":       # exit shell if command is "exit"
            os.write(1, ("Thank you for using the shell.\n").encode())
            break
        if "cd" in user_input:
            args = user_input.split()
            if args[0].strip() == "cd":
                if len(args) < 2:
                    continue
                if args[1].strip() == "..":
                    currentDir = os.getcwd()
                    newDir = currentDir.rsplit('/', 1)[0]
                    os.chdir(newDir)
                    continue
                else:
                    os.chdir(args[1].strip())
                    continue
        run_command(user_input)
        user_input = ""
        
os.write(1, ("Welcome to the shell.\n").encode())
e = os.environ
e["PS1"] = "$ "
startShell("", e)
