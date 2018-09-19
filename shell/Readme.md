# Writing a Shell in Python

I created this shell using Python 3. This shell should work with test scripts
and running it manually.

## Getting Started
In order to run this project successfully you will have to run the following
command in your shell:
```
$ python3 shell.py
```

## To run this shell you will need:
* Python 3.6
* Linux Command Line Terminal

## Shell Description
This shell will handle four different types of input. These types are: `single
command`, `input redirection`, `output redirection`, and `piping`.

### Single Command
When receiving the prompt, the user can enter a shell command and wait for the
results.

Example:

**Input**
```
$ uname
```
or
```
$ /bin/uname
```
**Output**
```
Linux
```

### Input Redirection
The shell will take the input entered by the user and run it with the first
part of the command. The result should not show the name of the file.

Input Redirection uses this symbol ` < ` to separate the main command from the
input file.

Example:

**Input**
```
$ wc < shell.py
```
**Output**
```
 123  417 4243
```

### Output Redirection
The shell will run the command entered by the user and write the results in
the file specified by the user.

Output Redirection uses this symbol ` > ` to separate the main command from
the ouput file.

Example:

**Input**
```
$ wc shell.py > output_shell.txt
```
**Output** (in output_shell.txt)
```
 123  417 2342 shell.py
```

### Piping
The shell will have two different commands/processes. The first one will be
writing and the second one reading. Then the second one can write while the
first one reads. The process repeats until one side stops writing.

Piping uses this symbol ` | ` to separate the two commands from each other.

**This is still not working**

Example:

**Input**
```
$ ls | sort -r
```
> Output
```
test_output.txt
shell.py
Readme.md
output_shell.txt
```

## That is the end of this lab.
