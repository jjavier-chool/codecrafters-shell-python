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
        append = False
        appendErr = False
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
            elif command_split[-2] in (">>", "1>>"):
                append = True
                outputFile = command_split[-1]
                command_split = command_split[:-2]
            elif command_split[-2] == "2>>":
                appendErr = True
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
                    output = f"cd: {abspath}: No such file or directory" + "\n" # Naive error, no msg for not a directory specifically
            case "echo":
                output = " ".join(command_split[1:]) + "\n"
            case "type":
                output, error = type(command[5:])
            case "pwd":
                output = os.getcwd() + "\n"
            case _:
                executable, _ = isExecutable(process)
                if executable:
                    if redirect or redirectErr or append or appendErr:
                        # Capture stdout if it's a redirect/append, or stderr if it's an error redirect/append
                        captureStdout = redirect or append
                        result = subprocess.run(
                            command_split,
                            stdout=subprocess.PIPE if captureStdout else None,
                            stderr=subprocess.PIPE if not captureStdout else None,
                            text=True
                        )
                        output = result.stdout if captureStdout else result.stderr
                        if not captureStdout and output:
                            error = True
                    else:
                        subprocess.run(command_split)

                else:
                    error = True
                    output = f"{command}: command not found" + "\n"
        if redirect or redirectErr:
            with open(outputFile, "w") as file:
                if redirectErr and not error:
                    sys.stderr.write(output)
                elif (redirect and not error) or (redirectErr and error):
                    file.write(output)
        elif append or appendErr:
            with open(outputFile, "a") as file:
                if appendErr and not error:
                    sys.stderr.write(output)
                elif (append and not error) or (appendErr and error):
                    file.write(output)
        else:
            sys.stdout.write(output)


if __name__ == "__main__":
    main()
