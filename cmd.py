import os
import sys
import redirect
import re
from colorama import Fore, Style,init

init(autoreset=True)

ps1 = None
quit_cmd = False

# update ps1 to cwd & color
def ps1_update():
    global ps1
    user = os.environ.get('USER')
    current_dir = os.getcwd()
    home_dir = os.environ['HOME']
    if current_dir == home_dir:
        display_dir = '~'
    else:
        display_dir = current_dir.replace(home_dir, '')
    '''
    # REQUIRED FOR ASSIGNMENT BUT NOT IMPLIMENTED:
    # NOT IMPLIMENTED BECAUSE I WANT TO SETUP PS1 TO LOOK GOOD
    # JUST UNCOMMENT TO IMPLIMENT AND COMMENT OUT OTHER PS1 ASSIGNMENT
    ps1 = f"{current_dir}\n{os.environ.get('PS1', '$ ')}"
    '''
    ps1 = Fore.GREEN + f"[{user}]" + Fore.BLUE + f"[{display_dir}]" + Style.RESET_ALL + '\n$ '

# set up ps1
ps1_update()
    

# handle directory changes
def cd_handler(cmd_lst):
    global ps1
    if len(cmd_lst) > 1:
        try:                                # attempt to change directory
            if cmd_lst[1] == '~':
                cmd_lst[1] = os.environ['HOME']
            os.chdir(cmd_lst[1])
        except (NotADirectoryError, FileNotFoundError, PermissionError) as e:
            print(f"fash: cd: {cmd_lst[1]}: {e}")
    else:                                   # cd -> home
        os.chdir(os.environ.get('HOME'))
    ps1_update()                            # keep ps1 up to date
    

# return command path if exists
def get_path(cmd):
    paths = os.environ.get("PATH").split(":")
    for path in paths:
        path += '/' + cmd
        try:
            f = open(path, "r")     # will read if it exists
            f.close()
            return path
        except FileNotFoundError:   # try another path
            continue
        except PermissionError as e:
            print(f"PermissionError: {e}")
            return None
    print(f"fash: {cmd}: command not found")
    return None
    
    
# return [binary executable path, arguments+]
def get_cmd_lst(arg):
    execCWD = arg.startswith('./')
    path=None
    cmd_lst = arg.split()
    if not cmd_lst:
        return None
    
    cmd = cmd_lst[0].lower()
    if not execCWD:
        path = get_path(cmd)
    
    if path or execCWD:
        # split cmd str respecting quoted sections
        split_pattern = r'''(?:
            (?P<quote>["'])(?P<quoted_text>.*?)(?P=quote) |  # match txt within quotes
            (?P<unquoted_text>[^"'\s]+)                      # match unquoted txt
        )'''
        matches = re.finditer(split_pattern, ' '.join(cmd_lst[1:]), re.VERBOSE)
        rest = []
        for match in matches:
            if match.group('quoted_text'):
                rest.append(match.group('quoted_text'))
            elif match.group('unquoted_text'):
                rest.append(match.group('unquoted_text'))
        return [cmd if execCWD else path] + rest
    return None


# create and execute a process
def run_process(cmd, input_file=None, output_file=None):
    try:
        cpid = os.fork()
        if cpid == 0:                   # child process
            try:
                if input_file or output_file:
                    redirect.redirect_io(input_file, output_file)
                os.execv(cmd[0], cmd)   # replace child process w/ command and its args
            except OSError as e:
                print(f"fash: {cmd[0]}: {e}.")
                sys.exit(1)
            except FileNotFoundError as e:
                print(f"fash: {e}")
                sys.exit(1)
        elif cpid < 0:
            print("Fork failed")
            sys.exit(1)
        return cpid                     # parent process
    except Exception as e:
        print(f"Error executing process: {e}")


# handles a string of cmd + arguments/parameters
def process_cmd(arg):
    global quit_cmd
    cmd_lst = arg.split()
    cmd = cmd_lst[0].lower()
    if cmd == 'quit':       # handle exit request
        print("Exiting..")
        quit_cmd = True
    elif cmd == 'cd':       # handle directory changes
        cd_handler(cmd_lst)
    else:
        handler(arg)        # handle regular commands


# process cmd based on type
def handler(arg):
    original_stdin = None
    original_stdout = None
    pType = 'bg' if arg.endswith('&') else 'fg'
    if pType == 'bg':
        arg = arg[:-1]
    cmd_lst, input_file, output_file = redirect.handler(arg)
    if cmd_lst:
        pid = run_process(cmd_lst, input_file, output_file)
        if pid:
            if pType == "fg":
                process_wait(pid)
            elif pType == "bg":
                print(f"{pid}")
                pass


# waits for a process to finish executing
def process_wait(pid):
    pid, status = os.waitpid(pid, 0)
    if not os.WIFEXITED(status):
        print(f"Program terminated: exit code {status}.")
        sys.exit(1)

