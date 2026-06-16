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
        return f"{command} is a shell builtin" + "\n", False
    elif executable:
        return f"{command} is {dir}" + "\n", False
    else:
        return f"{command}: not found" + "\n", True

def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_split = shlex.split(command)
        process = command_split[0]

        redirect = False
        redirectErr = False
        error = False
        output = ""
        outputFile = ""
        if len(command_split) >= 2:
            if command_split[-2] in (">", "1>"):
                redirect = True
                outputFile = command_split[-1]
                command_split = command_split[:-2]
            elif command_split[-2] == "2>":
                redirectErr = True
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
                    error = True
                    output = f"cd: {abspath}: No such file or directory" # Naive error, no msg for not a directory specifically
            case "echo":
                output = " ".join(command_split[1:]) + "\n"
            case "type":
                output, error = type(command[5:])
            case "pwd":
                output = os.getcwd() + "\n"
            case _:
                executable, _ = isExecutable(process)
                if executable:
                    if redirect:
                        result = subprocess.run(command_split, stdout=subprocess.PIPE, text=True)
                        output = result.stdout
                    elif redirectErr:
                        result = subprocess.run(command_split, stderr=subprocess.PIPE, text=True)
                        output = result.stderr
                        if output:
                            error = True
                    else:
                        subprocess.run(command_split)

                else:
                    print(f"{command}: command not found")
        if redirect or redirectErr:
            with open(outputFile, "w") as file:
                if redirect or (redirectErr and error):
                    file.write(output)
        else:
            sys.stdout.write(output)


if __name__ == "__main__":
    main()
