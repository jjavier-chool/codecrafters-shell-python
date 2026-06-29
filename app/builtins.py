# builtins.py
from __future__ import annotations
import os
import subprocess
from dataclasses import dataclass
from typing import Callable

@dataclass
class ShellContext:
    complete_map: dict[str, str]
    jobs_map: dict[int, tuple[subprocess.Popen, str]]


BuiltinFunction = Callable[
    [list[str], ShellContext],
    tuple[str, str]
]

BUILTINS = (
    "pwd",
    "type",
    "echo",
    "exit",
    "complete",
    "jobs",
    "cd",
)

def is_executable(command: str) -> tuple[bool, str]:
    path = os.environ.get("PATH", "")

    for directory in path.split(os.pathsep):
        executable = os.path.join(directory, command)

        if os.access(executable, os.X_OK):
            return True, executable

    return False, ""


def echo(args: list[str], _: ShellContext) -> tuple[str, str]:
    return " ".join(args) + "\n", ""


def pwd(_: list[str], __: ShellContext) -> tuple[str, str]:
    return os.getcwd() + "\n", ""


def cd(args: list[str], _: ShellContext) -> tuple[str, str]:
    path = args[0] if args else os.path.expanduser("~")

    if path == "~":
        path = os.path.expanduser("~")

    if os.path.isdir(path):
        os.chdir(path)
        return "", ""

    return "", f"cd: {path}: No such file or directory\n"


def type(args: list[str], _: ShellContext) -> tuple[str, str]:
    if not args:
        return "", ""

    command = args[0]

    if command in BUILTINS:
        return f"{command} is a shell builtin\n", ""

    executable, location = is_executable(command)

    if executable:
        return f"{command} is {location}\n", ""

    return "", f"{command}: not found\n"


def jobs(_: list[str], ctx: ShellContext) -> tuple[str, str]:
    out = ""
    dead: list[int] = []

    living = sorted(ctx.jobs_map.keys())

    plus = living[-1] if len(living) >= 1 else None
    minus = living[-2] if len(living) >= 2 else None

    for jobid, (process, command) in ctx.jobs_map.items():

        marker = ""

        if jobid == plus:
            marker = "+"
        elif jobid == minus:
            marker = "-"

        done = process.poll() is not None
        status = "Done" if done else "Running"

        out += (
            f"[{jobid}]"
            f"{marker}  "
            f"{status:<24}"
            f"{command}"
            f"{'' if done else ' &'}\n"
        )

        if done:
            dead.append(jobid)

    for jobid in dead:
        del ctx.jobs_map[jobid]

    return out, ""


def complete(args: list[str], ctx: ShellContext) -> tuple[str, str]:

    if len(args) < 2:
        return "", ""

    option = args[0]

    if option == "-p":

        command = args[1]

        if command in ctx.complete_map:
            return (
                f"complete -C '{ctx.complete_map[command]}' {command}\n",
                "",
            )

        return "", (
            f"complete: {command}: no completion specification\n"
        )

    if option == "-r":

        command = args[1]

        ctx.complete_map.pop(command, None)
        return "", ""

    if option == "-C":

        if len(args) < 3:
            return "", ""

        script = args[1]
        command = args[2]

        ctx.complete_map[command] = script
        return "", ""

    return "", ""


def shell_exit(_: list[str], __: ShellContext) -> tuple[str, str]:
    raise SystemExit(0)


BUILTIN_MAP: dict[str, BuiltinFunction] = {
    "echo": echo,
    "pwd": pwd,
    "cd": cd,
    "type": shell_type,
    "jobs": jobs,
    "complete": complete,
    "exit": shell_exit,
}