import subprocess
import shlex
import sys
import os

builtin = ["pwd", "type", "echo", "exit", "cat"]

def isExecutable(command):
    path = os.environ["PATH"]
    for dir in path.split(os.pathsep):
        if os.access(dir + "/" + command, os.X_OK):
            return True, dir + "/" + command
    return False, ""

def type(command):
    executable, dir = isExecutable(command)
    if command in builtin:
        print(f"{command} is a shell builtin")
    elif executable:
        print(f"{command} is {dir}")
    else:
        print(f"{command}: not found")

def cat(filenames):
    for file in filenames:
        try:
            with open(absolute_path, "r") as file:
            content = file.read()
            print(content)
        except FileNotFoundError:
            print("cat: {filename}: No such file or directory")


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_split = shlex.split(command)
        process = command_split[0]
        match process:
            case "exit":
                exit(0)
            case "cd":
                abspath = command[3:]
                if abspath == "~":
                    os.chdir(os.path.expanduser("~"))
                elif os.path.isdir(abspath):
                    os.chdir(abspath)
                else:
                    print(f"cd: {abspath}: No such file or directory") # Naive error, no msg for not a directory specifically
            case "echo":
                print(" ".join(command_split[1:]))
            case "type":
                type(command[5:])
            case "pwd":
                print(os.getcwd())
            case "cat":
                cat(command_split[1:])
            case _:
                executable, _ = isExecutable(process)
                if executable:
                    subprocess.run(command_split)
                else:
                    print(f"{command}: command not found")


if __name__ == "__main__":
    main()
