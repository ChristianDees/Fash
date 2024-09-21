import os
import sys
import redirect
from colorama import Fore, Style,init

init(autoreset=True)

ps1 = None
background_pids=[]
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

    ps1 = Fore.GREEN + f"[{user}]" + Fore.BLUE + f"[{display_dir}]" + Style.RESET_ALL + '\n$ '

# set up ps1
ps1_update()

# handle if exit request
def quit_handler():
    global quit_cmd
    if background_pids:                 # background process need cleaning
        print("There are background processes running.")
        inp = input("Are you sure you want to exit when there are processes running in the background? (y/n) ").strip()
        if inp == "n":
            quit_cmd = True
            return False
        elif inp == "y":                # wait for bg processes to finish
            for pid in background_pids:
                process_wait(pid)
    else:
        quit_cmd = True
    print("Exiting...")
    return True
    

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
def find_path(cmd):
    paths = os.environ.get("PATH").split(":")
    for path in paths:
        path += '/' + cmd
        try:
            f = open(path, "r")     # will read if it exists
            f.close()
            return path
        except FileNotFoundError:
            continue
    return None


# return [binary executable path, arguments+]
def get_cmd_lst(arg):
    cmd_lst = arg.split()
    if not cmd_lst:
        return None
    cmd = cmd_lst[0].lower()
    path = find_path(cmd)
    if path:
        return [path] + [cmd.replace('"', '') for cmd in cmd_lst[1:]]
    print(f"fash: {cmd}: command not found")
    return None


# create and execute a process
def run_process(cmd):
    try:
        cpid = os.fork()
        if cpid == 0:                   # child process
            try:
                os.execv(cmd[0], cmd)   # replace child process w/ command and its args
            except FileNotFoundError:
                print(f"Command not found: {command[0]}")
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
        handle_quit()
    elif cmd == 'cd':       # handle directory changes
        cd_handler(cmd_lst)
    else:
        handle_cmd(arg)     # handle regular commands


# exit check
def handle_quit():
    global quit_cmd
    if quit_handler():
        quit_cmd = True


# process cmd based on type
def handle_cmd(arg):
    filename, mode, flags, arg = parse_redirection(arg)
    cmd_lst = get_cmd_lst(arg)
    if cmd_lst:             # if arguments require redirection of i/o
        if filename:
            redirect.handler(cmd_lst, filename, mode, flags)
        else:               # regular arguments
            manage_process(cmd_lst, arg)


# return metadata required for redirection of i/o
def parse_redirection(arg):
    cidx = None
    filename = None
    flags = None
    mode = None
    if '<' in arg:              # setup input redirect
        cidx = arg.index('<')
        flags = os.O_RDONLY
        mode = 'in'
    elif '>' in arg:            # setup output redirect
        cidx = arg.index('>')
        flags = os.O_WRONLY | os.O_CREAT
        mode = 'out'
    if cidx is not None:        # obtain filename and args-filename
        filename = arg[cidx + 2:].strip()
        arg = arg[:cidx].strip()
    return filename, mode, flags, arg


# decides if process is background or foreground
def manage_process(cmd_lst, arg):
    pType = "bg" if arg.endswith('&') else "fg"
    pid = run_process(cmd_lst)
    if pType == "bg":
        background_pids.append(pid)
    elif pType == "fg":
        process_wait(pid)


# waits for a process to finish executing
def process_wait(pid):
    pid, status = os.waitpid(pid, 0)
    if not os.WIFEXITED(status):
        print(f"Program terminated: exit code {status}.")
        sys.exit(1)



def handler(prev_cmd, curr_cmd):
    prev_cmd_list = cmd.get_cmd_lst(prev_cmd)
    curr_cmd_list = cmd.get_cmd_lst(curr_cmd)
    try:
        r, w = os.pipe()
        cpid1 = os.fork()
        if cpid1 == 0:
            # Child process for the first command
            os.dup2(w, 1)  # Redirect stdout to write end of pipe
            os.close(r)
            os.close(w)
            os.execvp(prev_cmd_list[0], prev_cmd_list)  # Use execvp to find the command
        else:
            os.close(w)  # Parent closes the write end
            cpid2 = os.fork()
            if cpid2 == 0:
                # Child process for the second command
                os.dup2(r, 0)  # Redirect stdin to read end of pipe
                os.close(r)
                os.execvp(curr_cmd_list[0], curr_cmd_list)  # Use execvp to find the command
            else:
                os.close(r)  # Parent closes the read end
                os.waitpid(cpid1, 0)  # Wait for the first child
                os.waitpid(cpid2, 0)  # Wait for the second child
    except Exception as e:
        print(f"Error executing commands: {prev_cmd} | {curr_cmd}, Error: {e}")
