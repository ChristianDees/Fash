import os
import sys
import re

def findPath(command):
    paths = os.environ.get("PATH").split(":")
    for path in paths:
        path += '/' + command
        try:
            f = open(path, "r")
            f.close()
            return path
        except FileNotFoundError:
            continue
    return None

def processType(args):
    cmds = args.split(";")
    backgroundProcesses = []
    regularProcesses = []
   
    for cmd in cmds:
        # Extract commands that are meant to run in the background
        patternBP = r'[^&]*&'
        matchesBP = re.findall(patternBP, cmd)
       
        # Extract remaining commands which are not meant to be in the background
        cmd_cleaned = re.sub(patternBP, '', cmd).strip()  # Remove background commands from the original string
        if cmd_cleaned:
            regularProcesses = [cmd_cleaned]  # Assign the remaining commands as regular
        for match in matchesBP:
            backgroundProcesses.append(match[:-1].strip())
           
    return backgroundProcesses, regularProcesses

       

def runProcess(command):
    cpid = os.fork()
    if cpid == 0:
        # Child process
       
        try:
            # NEED TO CHANGE TO EXECV
            os.execv(command[0], command)
        except FileNotFoundError:
            print(f"Command not found: {command[0]}")
            sys.exit(1)
    # Parent process
    return cpid

if __name__ == "__main__":
    #ps1 = os.environ.get('PS1', '$ ')
    ps1=sys.path[0] +' $ '
    inp = None
    background_pids = []
    def cdHome():
         user_name = os.environ.get('USER') or os.environ.get('LOGNAME') or os.environ.get('USERNAME')
         userPath = f"/home/{user_name}"
         ps1 = userPath + ' $ '
         os.chdir(userPath)
         return ps1
               
    while inp != "quit":
        inp = input(ps1).strip()
        args = inp.split()
        if not args or args[0] == "#":
            continue
        elif args[0] == "quit":
            break
        elif args[0] == "cd":
            if len(args) > 1:
                try:
                    os.chdir(args[1])
                    if (args[1][0] == '/'):
                        ps1 = args[1] + ' $ '
                    elif (args[1] == '.'):
                        ps1 = goHome()
                    elif ('..' in args[1]):
                        totalCount = args[1].count('..')
                        paths=ps1.split('/')
                        start = len(paths)-1
                        end = start-totalCount
                       
                        for i in range(start, end, -1):
                            if len(paths)==2:
                                paths[1] = ''
                                break
                            del paths[i]
                        ps1 = '/'.join(paths) + ' $ '
                         
                    else:
                        cwd = ps1.split(" ")[0]
                        if args[1].endswith('/'):
                            args[1] = args[1][:-1]
                        if (cwd.endswith('/')):
                            cwd+=args[1]
                        else:
                            cwd+='/'+args[1]
                        ps1 = cwd + ' $ '
                       
                   
                   
                except NotADirectoryError:
                    print(f"fash: cd: {args[1]}: Not a directory")
                except FileNotFoundError:
                    print(f"fash: cd: {args[1]}: No such file or directory")
                except PermissionError:
                    print(f"Permission denied: {args[1]}")
            else:
                ps1 = cdHome()
        else:
            path = findPath(args[0])
            commandList = [path, args[1:]]
            bgp, rp = processType(inp)
            for process in bgp:
                cmds = process.split()
                path = findPath(cmds[0])
                if len(cmds)>1:
                    commandList = [path, ' '.join(cmds[1:])]
                else:
                    commandList = [path]
                #print(f"COMANDLIST: {commandList}")
                if path:
                    pid = runProcess(commandList)
                    background_pids.append(pid)
                    print(f"[{len(background_pids)}] {pid}")
                else:
                    print("Command not found")
               
            for process in rp:
                cmds = process.split()
                path = findPath(cmds[0])
               
                if len(cmds)>1:
                    commandList = [path, ' '.join(cmds[1:])]
                else:
                    commandList = [path]
                #print(f"COMANDLIST: {commandList}")
                if path:
                    runProcess(commandList)            
                    os.wait()
                else:
                    print("Command not found")

    while background_pids:
        try:
            pid, status = os.wait()  # Wait for any child process to complete
            if pid in background_pids:
                background_pids.remove(pid)
        except ChildProcessError:
            break
