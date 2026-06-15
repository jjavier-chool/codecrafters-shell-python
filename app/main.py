import subprocess
import sys
import os

builtin = ["pwd", "type", "echo", "exit"]

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

def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_split = command.split()
        process = command_split[0]
        executable, dir = isExecutable(process)
        match process:
            case "exit":
                exit(0)
            case "cd":
                if command[3:] == "~":
                    os.chdir(os.path.expanduser("~"))
                elif os.path.isdir(command[3:]):
                    os.chdir(command[3:])
                else:
                    print(f"cd: {command[3:]}: No such file or directory") # Naive error, no msg for not a directory specifically
            case "echo":
                print(command[5:])
            case "type":
                type(command[5:])
            case "pwd":
                print(os.getcwd())
            case _:
                if executable:
                    subprocess.run(command_split)
                else:
                    print(f"{command}: command not found")


if __name__ == "__main__":
    main()
