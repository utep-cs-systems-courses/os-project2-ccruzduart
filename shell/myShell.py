#! /usr/bin/env python3
#
# myShell.py
#
# Made by: Cristian Cruz

import os, sys, re
from os import read,write

def readLine():
    i = 0
    line = ""
    buff = read(0,100)
    string = buff.decode()

    while i < len(string):
        char = string[i]
        if char == '\n':
            return line
        line += char
        i += 1

        if i >= 100:
            buff = read(0,100)
            string = buff.decode()
            i = 0

    return ""

def redirect(arg, symbol):
    if symbol == '<' and arg.count("<") == 1:
        os.close(0)
        os.open(arg[arg.index(symbol)+1],os.O_RDONLY)
        os.set_inheritable(0,True)
    elif symbol == '>' and arg.count(">") == 1:
        os.close(1)
        os.open(arg[arg.index(symbol)+1],os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)
    else:
        os.write(2,"redirect error".encode())
        sys.exit(1)

def pipe(args):
    pread, pwrite = os.pipe()
    child = os.fork()

    if child < 0:
        os.write(2, "fork failed".encode())
        sys.exit(1)
    elif child == 0:
        os.close(1)
        os.dup(pwrite)
        os.set_inheritable(1,True)

        for fileDescripter in (pread, pwrite):
            os.close(fileDescripter)

        leftArgs = args[:args.index('|')]

        if '<' in leftArgs:
            redirect(leftArgs, '<')

        try:
            os.execve(leftArgs[0], leftArgs, os.environ)
        except FileNotFoundError:
            pass

        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir,leftArgs[0])

            try:
                os.execve(program, leftArgs, os.environ)
            except FileNotFoundError:
                pass

        os.write(w,("Could not exec: %s\n" % leftArgs[0]).encode())
        sys.exit(1)

    else:
        os.close(0)
        os.dup(pread)
        os.set_inheritable(0,True)

        for fileDescriptor in (pwrite, pread):
            os.close(fileDescriptor)

        rightArgs = args[args.index('|')+1:]

        if '>' in rightArgs:
            redirect(rightArgs, '>')

        for directory in re.split(":",os.environ['PATH']):
            program = "%s/%s" % (directory, rightArgs[0])

            try:
                os.execve(program, rightArgs, os.environ)
            except FileNotFoundError:
                pass

        os.write(2,("Could not exec: %s\n" % rightArgs[0]).encode())
        sys.exit(1)

while True:
    if 'PS1' in os.environ:
        os.write(2, (os.environ['PS1']).encode())
    else:
        os.write(2,"$ ".encode())

    args = readLine().strip().split(" ")

    if args[0] == "":
        continue
    elif args[0] == "exit":
        sys.exit(0)
    elif args[0] == "cd":
        if len(args)>1:
            try:
                os.chdir(args[1])
                continue
            except:
                cwd = os.getcwd()
                print("Current working directory %s"%cwd)
                os.write(2,"No such directory\n".encode())
                continue
        else:
             os.system(args[0])
             continue
        continue

    child = os.fork()

    hold = True
    if '&' in args:
        hold = False
        args.remove('&')

    if child < 0:
        os.write(2, "fork failed".encode())
        sys.exit(0)
    elif child == 0:
        if '|' in args:
            pipe(args)
            continue
        if '<' in args:
            print("checking <")
            redirect(args,'<')
        if '>' in args:
            print("checking >")
            redirect(args,'>')

        try:
            os.execve(args[0], args, os.environ)
        except Exception as e:
            pass

        for directory in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (directory, args[0])

            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass

        os.write(2,("Could not exec: %s\n"%args[0]).encode())
        sys.exit(1)

    elif hold:
        childPid = os.wait()
