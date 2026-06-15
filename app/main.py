import sys

builtin = ["type", "echo", "exit"]

def getPath(command):
    path = os.environ["PATH"]
    for dir in path.split(":"):
        if os.access(dir + "/" + command, os.X_OK):
            return dir + "/" + command
    return ""


def isExecutable(command):
    path = os.environ["PATH"]
    for dir in path.split(os.pathsep):
        if os.access(dir + "/" + command, os.X_OK):
            return True, dir + "/" + command
    return False, ""

def type(command):
    executable, dir = isExecutable(command)
    if command in builtin:
        print(f"{typed_command} is a shell builtin")
    elif executable:
        print(f"{command} is {dir}")
    else:
        print(f"{typed_command}: not found")

def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        command_split = command.split()
        process = command_split[0]
        match process:
            case "exit":
                exit(0)
            case "echo":
                print(command[5:])
            case "type":
                type(command[5:])
            case _:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()
