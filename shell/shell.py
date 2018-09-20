#! /usr/bin/env python3

import os, sys, time, re, fileinput

def run_execve(args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        program = "%s/%s" % (dir, args[0].strip())
        try:
            os.execve(program, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly
        
def getPipeInfo(user_input):
    processes = user_input.split(' | ')
    args = processes[0].split()
    pipeFlag = True
    return processes, args, pipeFlag

def getOutputInfo(user_input):
    args = user_input.split(' > ')
    outputFlag = True
    output_file = args[len(args)-1].strip()
    folder = ""
    if "/" in output_file:     # check if output file has a specified folder
        folder = output_file.split("/")[1]
        output_file = output_file.split("/")[2]
        try:
            os.mkdir(folder)
        except:
            pass
    if ".txt" not in output_file:            # add .txt to files that don't have it
        output_file = output_file + ".txt"
    args = args[0].split()
    return args, outputFlag, output_file, folder

def getInputInfo(user_input):
    args = user_input.split(' < ')
    inputFlag = True
    args[len(args)-1] = args[len(args)-1].strip()
    return args, inputFlag

def basicCommands(user_input):
    args = user_input.split()
    if "/bin/" in args[0]:
        args[0] = args[0].replace("/bin/", "")
    return args
        
def outputRedirect(args, folder, output_file):
    os.close(1)                 # redirect child's stdout
    if folder == "":
        sys.stdout = open(output_file, "w")  # write on file
    else:
        newPath = os.getcwd() + "/" + folder + "/" + output_file
        sys.stdout = open(newPath, "w")  # write on file
        
    os.set_inheritable(1, True)
    return sys.stdout

def inputRedirect(args):
    os.close(0)
    sys.stdin = open(args[len(args)-1], "r")   # read from file
    os.set_inheritable(0, True)
    args = [args[0]]
    return sys.stdin, args

def pipes(args, processes):
    pr, pw = os.pipe()      # file descriptors pr, pw for reading and writing
    for f in (pr, pw):
        os.set_inheritable(f, True)
    pipeFork = os.fork()   # begin forking
    
    if pipeFork < 0:     # fork failed
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
        
    if pipeFork == 0:    # child
        os.close(1)
        os.dup(pw)
        os.set_inheritable(1, True)  # make duplicate file descriptor inheritable
        for fd in (pr, pw):
            os.close(fd)
        run_execve(args)    # run first process and send to parent
        
    else:               # parent
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)   # make duplicate file descriptor inheritable
        for fd in (pw, pr):
            os.close(fd)
        run_execve(processes[1].split())   # read process result from child and run second process
    
def run_command(user_input):
    pid = os.getpid()               # get and remember parent pid
    
    inputFlag = outputFlag = pipeFlag = False

    # check if there's redirection or piping and get commands
    if ' | ' in user_input:
        processes, args, pipeFlag = getPipeInfo(user_input)
        
    elif ' > ' in user_input:
        args, outputFlag, output_file, folder = getOutputInfo(user_input)
        
    elif ' < ' in user_input:
        args, inputFlag = getInputInfo(user_input)

    else:
        args = basicCommands(user_input)

    rc = os.fork()    # begin forking

    if rc < 0:      #fork failed
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:      # child
            
        if outputFlag:
            sys.stdout = outputRedirect(args, folder, output_file)

        if inputFlag:
            sys.stdin, args = inputRedirect(args)
            
        if pipeFlag:
            pipes(args, processes)
                
        if not pipeFlag:
            run_execve(args)
        os.write(2, ("Command not found.\n").encode())
        sys.exit(1)                 # terminate with error 1

    else:            # parent (forked ok)
        os.wait()   # wait for child to terminate
            
def startShell(user_input, e):
    while True:
        if user_input == "" or user_input == " " or "cd" in user_input:
            #user_input = input("$ ")
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
e["PS1"] = ""
startShell("", e)
