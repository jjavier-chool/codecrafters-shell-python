import sys


def main():
    while True:
        sys.stdout.write("$ ")
        usr_input = input()
        if usr_input == "exit":
            break
        elif usr_input.startswith("echo "):
            print(command[5:])
        else:
            print(f"{command}: command not found")
    pass


if __name__ == "__main__":
    main()
