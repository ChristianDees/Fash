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

def runProcess(command):
    try:
        cpid = os.fork()
        if cpid == 0:
            # Child process
            try:
                os.execv(command[0], command)
            except FileNotFoundError:
                print(f"Command not found: {command[0]}")
                sys.exit(1)
        # Parent process
        return cpid
    except Exception as e:
        print(f"Error executing process: {e}")




def handleRedirect(cmd, filename, mode, flags):
    try:
        pid = os.fork()
        if pid == 0:
            try:
                fd = os.open(filename, flags)
                if mode == 'in':
                    os.dup2(fd, 0)  # Redirect stdin
                elif mode == 'out':
                    os.dup2(fd, 1)  # Redirect stdout
                os.close(fd)  
                os.execv(cmd[0], cmd)
            except Exception as e:
                print(f"Error: {str(e)}")
                return 1
        elif pid > 0:
            pid, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status):
                return os.WEXITSTATUS(status)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1







def main():
    try:
        ps1 = os.getcwd() + ' $ '
        inp = None
        
        background_pids = []
                   
        while True:
            inp = input(ps1).strip()
            if not inp:
                continue
            
            ignorePat = r'#\s*([^;\n]+?)(?:;|$)'
            inp = re.sub(ignorePat, ';', inp).strip(';')
            splitPat = r';(?=(?:[^\'"]*\'[^\'"]*\')*[^\'"]*$)'
            args = re.split(splitPat, inp)
            
            for arg in args:
                arg = arg.replace("'",'')
                cmdList = arg.split()
                if not cmdList:
                    continue
                
                cmd = cmdList[0].lower()
                cidx = None
                filename = None
                flags = None
                mode = None
                
                if cmd == 'quit':
                    if background_pids:
                        print("There are background processes running.")
                        inp = input("Are you sure you want to exit when there are processes running in the background? (y/n) ").strip()
                        if inp == "n":
                            continue
                        elif inp == "y":

                            for pid in background_pids:
                                os.waitpid(pid, 0)
                    print("Exiting..")
                    return
                
                elif cmd == 'cd':
                    if len(cmdList) > 1:
                        try:
                            os.chdir(cmdList[1])
                        except (NotADirectoryError, FileNotFoundError, PermissionError) as e:
                            print(f"fash: cd: {cmdList[1]}: {str(e)}")
                            continue
                    else:
                        os.chdir(os.environ.get('HOME'))
                    ps1 = os.getcwd() + ' $ '
                    
                elif '<' in arg:
                    cidx = arg.index('<')
                    flags = os.O_RDONLY
                    mode = 'in'
                elif '>' in arg:
                    cidx = arg.index('>')
                    flags = os.O_WRONLY | os.O_CREAT
                    mode = 'out'
                    
                if cidx:
                    filename = arg[cidx+2:]
                    arg = arg[:cidx]
                    
                cmdList = arg.split()
                if not cmdList:
                    continue
                
                cmd = cmdList[0].lower()
                path = findPath(cmd)
                if path:
                    commandList = [path] + cmdList[1:]
                    if filename:
                        handleRedirect(commandList, filename, mode, flags)
                    else:
                        pType = "bg" if arg.endswith('&') else "fg"
                        pid = runProcess(commandList)
                        if pType == "bg":
                            background_pids.append(pid)
                        elif pType == "fg":
                            pid, status = os.waitpid(pid, 0)
                            if not os.WIFEXITED(status):
                                print(f"Program terminated: exit code {status}.")
                                sys.exit(1)
                else:
                    print(f"fash: {cmd}: command not found")
                
    except KeyboardInterrupt:
        print("\nExited on KeyboardInterrupt")
        sys.exit(0)

  
        
if __name__ == "__main__":
    main()
