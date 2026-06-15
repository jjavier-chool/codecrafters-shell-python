import sys

def type(command):
    match command:
        case "exit" | "echo" | "type":
            print(f"{command} is a shell builtin.")
        case _:
            print(f"{command}: not found")

def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            break
        elif command.startswith("echo "):
            print(command[5:])
        elif command.startswith("type "):
            type(command[5:])
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
