import sys


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        match command:
            case "exit":
                break
            case _:
                print(f"{command}: command not found")
    pass


if __name__ == "__main__":
    main()
