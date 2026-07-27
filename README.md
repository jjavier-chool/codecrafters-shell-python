[![progress-banner](https://backend.codecrafters.io/progress/shell/773557e8-7892-4047-a047-88c001472598)](https://app.codecrafters.io/users/jjavier-chool?r=2qF)

This is a starting point for Python solutions to the
["Build Your Own Shell" Challenge](https://app.codecrafters.io/courses/shell/overview).

Challenge description: build your own POSIX compliant shell that's capable of
interpreting shell commands, running external programs and builtin commands like
cd, pwd, echo and more. Along the way, you'll learn about shell command parsing,
REPLs, builtin commands, and more.

# TODO:
- Refractor; files for built-ins and autocomplete. Get an agent to do this for me?
- Reinventing the wheel isn't necessary, but looking into my own attempts at what shlex and readline can accomplish

# Notes: documentation for utilized libraries

- [sys](https://docs.python.org/3/library/sys.html)
- [os](https://docs.python.org/3/library/os.html#module-os)
- [os.path](https://docs.python.org/3/library/os.path.html#module-os.path) 
- [shlex](https://docs.python.org/3/library/shlex.html)
- [subprocess](https://docs.python.org/3/library/subprocess.html)
- [readline](https://docs.python.org/3/library/readline.html)

# Task completion

1. Ensure `uv` is installed locally
1. Run `./your_program.sh` to run the program, which is implemented in
   `app/main.py`.
1. Run `codecrafters submit` to submit a solution to CodeCrafters. Test
   output will be streamed to the terminal.
