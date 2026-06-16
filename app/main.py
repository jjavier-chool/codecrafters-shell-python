import subprocess
import shlex # This library is basically like cheating for all of the quoting challenges. Want to try writing it myself later
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
        return f"{command} is a shell builtin"
    elif executable:
        return f"{command} is {dir}"
    else:
        return f"{command}: not found"

def cat(filenames):
    output = ""
    for filename in filenames:
        try:
            with open(filename, "r") as file:
                content = file.read()
                output += content
        except FileNotFoundError:
            return f"cat: {filename}: No such file or directory"
    return output


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_split = shlex.split(command)
        process = command_split[0]

        redirect = False
        output = ""
        outputFile = ""
        if command_split[-2] == ">" | command_split[-2] == "1>":
            redirect = True
            outputFile = command_split[-1]

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
                ouput = " ".join(command_split[1:])
            case "type":
                output = type(command[5:])
            case "pwd":
                output = os.getcwd()
            case "cat":
                output = cat(command_split[1:])
            case "ls":
                output = os.listdir('.')
            case _:
                executable, _ = isExecutable(process)
                if executable:
                    subprocess.run(command_split)
                    # not sure how to redirect output here yet
                else:
                    print(f"{command}: command not found")
        if redirect:
            with open(outputFile, "w") as file:
                file.write(output)


if __name__ == "__main__":
    main()
