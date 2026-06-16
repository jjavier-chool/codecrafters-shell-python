import subprocess
import readline
import shlex # This library is basically like cheating for the quoting challenges. Want to try writing it myself later
import sys
import os

# Currently defined built-in commands
builtin = ["pwd", "type", "echo", "exit"]

def completer(text: str, state: int) -> str | None:
    """Tab autocompletion

    This function finds a matching built-in command according to the given prefix and state.

    Args:
        text (str): The given user text.
        state (int): The index of the current matching command, incremented by readline.

    Returns:
        str: The name of the matching built-in command.
        None: No matching built-in command found.
    """
    matches = [command for command in builtin if command.startswith(text)]

    if state < len(matches):
        return matches[state] + " "

    return None

def isExecutable(command: str) -> tuple[bool, str]:
    """Determines whether a given command is executable

    This function searches for an executable file with the given name.

    Args:
        command (str): The given command to investigate.

    Returns:
        tuple[bool, str]: T/F whether the command is executable, the command's path
    """
    path = os.environ["PATH"]
    for dir in path.split(os.pathsep):
        if os.access(dir + "/" + command, os.X_OK):
            return True, dir + "/" + command
    return False, ""

def type(command: str) -> tuple[str, bool]:
    """Type built-in

    This function determines the type of the given command: builtin, executable, or not found.

    Args:
        command (str): The command requested by the user

    Returns:
        tuple[str, bool]: The proper type reporting, T/F whether the command was found
    """
    executable, dir = isExecutable(command)
    if command in builtin:
        return f"{command} is a shell builtin" + "\n", False
    elif executable:
        return f"{command} is {dir}" + "\n", False
    else:
        return f"{command}: not found" + "\n", True

def main() -> None:
    """Main parsing logic of Shell

    This function performs the majority of the required logic. Parses user input,
    performs built-in processes when necessary, or executes a given process if found.
    Redirects to files when specified by user input.

    """
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        # Print $ and obtain user input.
        sys.stdout.write("$ ")
        command = input()
        if not command:
            continue
        command_split = shlex.split(command)
        process = command_split[0]

        # Checking if there are requested stdout and stderr redirects to files.
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

        # Performing the user's given process.
        match process:
            case "exit":
                exit(0)
            case "echo":
                output = " ".join(command_split[1:]) + "\n"
            case "type":
                output, error = type(command[5:])
            case "pwd":
                output = os.getcwd() + "\n"
            case "cd":
                abspath = command[3:]
                if abspath == "~":
                    os.chdir(os.path.expanduser("~"))
                elif os.path.isdir(abspath):
                    os.chdir(abspath)
                else:
                    error = True
                    # Naive error: no specific message given for non-directory
                    output = f"cd: {abspath}: No such file or directory" + "\n"
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

        # Perform redirecting/appending, or write to stdout.
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
