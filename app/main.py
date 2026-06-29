# main.py
import subprocess
import readline
import shlex
import sys
import os

# Currently defined built-in commands
builtin = ["pwd", "type", "echo", "exit", "complete", "jobs"]
# User's registered complete scripts
complete_map: dict[str, str] = {}
# Current background jobs
jobs_map: dict[int, (subprocess.Popen, str)] = {}

def get_completions(prefix: str) -> list[str]:
  """Gather all matching executables

  Args:
      prefix (str): the user's inputted string to complete

  Returns:
      list[str]: the sorted list of command names

  Exception:
      PermissionError: not allowed to read file/directory
      FileNotFoundError: file/directory DNE
  """
  # Set to automatically remove duplicates
  matches = set()

  # Built-ins
  for b in builtin:
    if b.startswith(prefix):
      matches.add(b)

  # External executables
  path_env = os.environ.get("PATH", "")
  for directory in path_env.split(os.pathsep):
    # Skip if the path isn't a valid directory
    if not os.path.isdir(directory):
      continue
    try:
      # Every file in this directory
      for filename in os.listdir(directory):
        if filename.startswith(prefix):
          filepath = os.path.join(directory, filename)
          # Verify file is executable
          if os.access(filepath, os.X_OK):
            matches.add(filename)
    except (PermissionError, FileNotFoundError):
      continue

  # Sort so they appear alphabetically
  return sorted(list(matches))

def get_file_completions(prefix: str) -> list[str]:
  """Gather all matching files and directories

  Args:
    prefix (str): The user's inputted filepath string

  Returns:
    list[str]: The sorted list of matching files/directories
  
  Exception:
    PermissionError: not allowed to read file/directory
    FileNotFoundError: file/directory DNE
  """
  # Split the prefix into directory and the partial filename
  # e.g., "src/ma" -> dir_name="src", base_name="ma"
  dir_name = os.path.dirname(prefix)
  base_name = os.path.basename(prefix)

  # If no directory was typed, search the current directory
  search_dir = dir_name if dir_name else "."

  matches = []
  try:
    for filename in os.listdir(search_dir):
      if filename.startswith(base_name):
        # Reconstruct the path exactly as the user typed it
        if dir_name:
          matches.append(os.path.join(dir_name, filename))
        else:
          matches.append(filename)
  except (FileNotFoundError, PermissionError):
    pass

  return sorted(matches)

def get_script_completions(script_path: str, cmd_name: str, current_word: str, prev_word: str, full_line: str) -> list[str]:
  """Executes an external autocomplete script and parses its output lines

  Args:
    script_path (str): path to the completer script
    cmd_name (str): argv[1] command name
    current_word (str): argv[2] current word being completed
    prev_word (str): argv[3] preceding word (or empty string)
    full_line (str): The entire string inside the prompt buffer

  Returns:
    list[str]: list of completion candidates from each line of output
  
  Exception:
    pass any exceptions
  """
  try:
    env = os.environ.copy()
    env["COMP_LINE"] = full_line
    env["COMP_POINT"] = str(len(full_line))
    result = subprocess.run(
      [script_path, cmd_name, current_word, prev_word],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
      env=env
    )
    if result.stdout:
      return sorted(result.stdout.split())

  except Exception:
    pass

  return []

def completer(text: str, state: int) -> str | None:
  """Tab autocompletion

  Args:
    text (str): The given user text.
    state (int): The index of the current matching command, incremented by readline.

  Returns:
    str: The name of the matching built-in command.
    None: No matching built-in command found.
  """
  line = readline.get_line_buffer()
  if line.lstrip() == text:
    matches = get_completions(text)
  else:
    # Split text before cursor to get preceding word and command
    end_idx = readline.get_begidx()
    text_before_cursor = line[:end_idx]
    tokens_before = text_before_cursor.split()
    first_command = tokens_before[0] if tokens_before else ""
    prev_word = tokens_before[-1] if tokens_before else ""

    if first_command in complete_map:
      script_file = complete_map[first_command]
      matches = get_script_completions(script_file, first_command, text, prev_word, line)
    else:
      matches = get_file_completions(text)

  if state < len(matches):
    match = matches[state]
    if os.path.isdir(match):
      return match + "/"
    else:
      return match + " "

  return None

def display_matches(substitution: str, matches: list[str], longest_match_len: int) -> None:
  """Print list of matches

  Args:
      substitution (str): longest common prefix that all matches share
      matches (list[str]): the list of matched commands to the user's prefix
      longest_match_len (int): length of the longest match string
  """
  print()
  print("  ".join(sorted(matches)))

  sys.stdout.write("$ " + readline.get_line_buffer())
  sys.stdout.flush()

def isExecutable(command: str) -> tuple[bool, str]:
  """Determines whether a given command is executable

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

def shell_type(command: str) -> tuple[str, bool]:
  """Type built-in

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

def jobs(called: bool) -> str:
  """Jobs built-in

  Args:
    called (bool): Whether being called at the end of the loop or by user

  Returns:
    str: the full jobs report
  """
  out_text = ""
  to_delete = []
  living_ids = sorted(jobs_map.keys())
  plus_id  = living_ids[-1] if len(living_ids) >= 1 else None
  minus_id = living_ids[-2] if len(living_ids) >= 2 else None

  for count, (bgprocess, command) in jobs_map.items():
    schar = ''
    if count == plus_id:
      schar = '+'
    elif count == minus_id:
      schar = '-'

    is_done = bgprocess.poll() is not None
    status = 'Done' if is_done else 'Running'

    if (not called and is_done) or called:
      out_text += f"[{count}]{schar}  {status:<24}{command}{'' if is_done else ' &'}\n"

    if is_done:
      to_delete.append(count)

  for dead_id in to_delete:
    del jobs_map[dead_id]

  return out_text

def run_builtin(command_split: list[str]) -> tuple[str, str]:
  """

  """
  if not command_split or not command_split[0]:
    return "", ""

  process = command_split[0]

  match process:
    case "exit":
      exit(0)
    case "echo":
      return " ".join(command_split[1:]) + "\n", ""
    case "type":
      out_text, error = shell_type(command_split[1])
      if error:
        return "", out_text
      else:
        return out_text, ""
    case "pwd":
      return os.getcwd() + "\n", ""
    case "jobs":
      return jobs(True), ""
    case "cd":
      abspath = command_split[1]
      if abspath == "~":
        os.chdir(os.path.expanduser("~"))
      elif os.path.isdir(abspath):
        os.chdir(abspath)
      else:
        return "", f"cd: {abspath}: No such file or directory" + "\n"
    case "complete":
      if len(command_split) > 2:
        if command_split[1] == "-p":
          if command_split[2] in complete_map:
            return f"complete -C '{complete_map[command_split[2]]}' {command_split[2]}" + "\n", ""
          else:
            return "", f"complete: {command_split[2]}: no completion specification" + "\n"
        elif command_split[1] == "-r" and command_split[2] in complete_map:
          del complete_map[command_split[2]]
        elif command_split[1] == "-C" and len(command_split) > 3:
          complete_map[command_split[3]] = command_split[2]
  return "", ""

def run_command(command_split: list[str], stdin_data: str = "", background: bool = False,) -> tuple[str, str]:
  """Executes an external command.

  Args:
    command_split: Command and arguments
    stdin_data: Data to provide on stdin (used by pipelines)
    background: Whether to execute in the background

  Returns:
    tuple[str, str]: (stdout, stderr) strings
    """
  if not command_split or not command_split[0]:
    return "", ""

  process = command_split[0]

  executable, _ = isExecutable(process)

  if not executable:
    return "", f"{process}: command not found\n"

  if background:
    bgprocess = subprocess.Popen(command_split)
    jobid = max(jobs_map) + 1 if jobs_map else 1
    jobs_map[jobid] = (bgprocess, " ".join(command_split))

    return f"[{jobid}] {bgprocess.pid}\n", ""

  result = subprocess.run(
    command_split,
    input=stdin_data,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
  )

  return result.stdout, result.stderr

def handle_pipeline(command_split: list[str]) -> tuple[str, str]:
  segments: list[list[str]] = []
  current: list[str] = []

  for token in command_split:
    if token == "|":
      if current:
        segments.append(current)
      current = []
    else:
      current.append(token)

  if current:
    segments.append(current)

  prev_process = None
  final_err = ""

  for i, segment in enumerate(segments):

    cmd = segment[0]

    if cmd in builtin:
      out, err = run_builtin(segment)

      prev_process = out
      final_err += err
      continue

    if prev_process is None or isinstance(prev_process, str):
      p1 = subprocess.Popen(
        segment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
      )

      input_data = prev_process if isinstance(prev_process, str) else None

      prev_process = p1
      out, err = p1.communicate(input=input_data)

      prev_process = out
      final_err += err

    else:
      p2 = subprocess.Popen(
        segment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
      )

      out, err = p2.communicate(input=prev_process)

      prev_process = out
      final_err += err

  return prev_process or "", final_err

def main() -> None:
  readline.set_completer(completer)
  readline.parse_and_bind("tab: complete")
  readline.set_completion_display_matches_hook(display_matches)
  readline.set_completer_delims(" \t\n")

  while True:
    sys.stdout.write("$ ")
    command = input()

    if not command:
      bg = jobs(False)
      if bg:
        sys.stdout.write(bg)
        sys.stdout.flush()
      continue

    command_split = shlex.split(command)

    redirect = False
    redirectErr = False
    append = False
    appendErr = False
    background = False
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
      elif command_split[-1] == "&":
        background = True
        command_split = command_split[:-1]

    out_text = ""
    err_text = ""

    if "|" in command_split:
      out_text, err_text = handle_pipeline(command_split)
    else:
      if command_split[0] in builtin:
        out_text, err_text = run_builtin(command_split)
      else:
        out_text, err_text = run_command(
          command_split,
          background=background,
        )

    if redirect or append:
      mode = "a" if append else "w"
      with open(outputFile, mode) as f:
        f.write(out_text)
    else:
      sys.stdout.write(out_text)

    if redirectErr or appendErr:
      mode = "a" if appendErr else "w"
      with open(outputFile, mode) as f:
        f.write(err_text)
    else:
        sys.stderr.write(err_text)

    bg = jobs(False)
    if bg:
      sys.stdout.write(bg)
      sys.stdout.flush()

if __name__ == "__main__":
  main()
