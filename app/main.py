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

def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_split = shlex.split(command)
        process = command_split[0]

        redirect = False
        output = ""
        outputFile = ""
        if (command_split[-2] == ">") | (command_split[-2] == "1>"):
            redirect = True
            outputFile = command_split[-1]
            command_split = command_split[:-2]

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
                output = " ".join(command_split[1:]) + "\n"
            case "type":
                output = type(command[5:]) + "\n"
            case "pwd":
                output = os.getcwd() + "\n"
            case _:
                executable, _ = isExecutable(process)
                if executable:
                    # text=True returns a string instead of bytes
                    # capture_output=True grabs stdout so we can save it to a variable
                    result = subprocess.run(command_split, capture_output=True, text=True)
                    output = result.stdout
                else:
                    print(f"{command}: command not found")
        if redirect:
            with open(outputFile, "w") as file:
                file.write(output)
        else:
            sys.stdout.write(output)


if __name__ == "__main__":
    main()
