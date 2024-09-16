'''
Christian Dees
University of Texas at El Paso
Operating Systems
Dr. Ward
September 16, 2024
This program is an ineratice shell for a Unix-based system
'''


# library constraints
import os
import sys
import re


# globals
ps1 = os.getcwd() + ' $ '
background_pids=[]
quitCmd = False


# return command path if exists
def findPath(command):
    paths = os.environ.get("PATH").split(":")
    for path in paths:
        path += '/' + command
        try:
            # will read if it exists
            f = open(path, "r")
            f.close()
            return path
        except FileNotFoundError:
            continue
    return None


# create and execute a process 
def runProcess(command):
    try:
        cpid = os.fork()
        if cpid == 0:
            # child process
            try:
                # replace child process w/ command and its args
                os.execv(command[0], command)
            except FileNotFoundError:
                print(f"Command not found: {command[0]}")
                sys.exit(1)
        # parent process
        return cpid
    except Exception as e:
        print(f"Error executing process: {e}")


# handle i/o redirection
def handleRedirect(cmd, filename, mode, flags):
    try:
        pid = os.fork()
        # child process
        if pid == 0:
            # get file descriptor cat < example.txt
            fd = os.open(filename, flags)
            # duplicate fd to i/o of file
            # 0 = std input, 1 std output
            os.dup2(fd, 0 if mode == 'in' else 1)
            os.close(fd)  
            os.execv(cmd[0], cmd)
        elif pid > 0:
            # parent process let child finish
            pid, status = os.waitpid(pid, 0)
            if os.WIFEXITED(status):
                exitCode = os.WEXITSTATUS(status)
                if exitCode != 0:
                    # return exit code if failed
                    return exitCode
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


# create list of args from inp
def getArgs(inp):
    args =[]
    # ignore strings started with # and possibly end in ;
    ignorePat = r'#\s*([^;\n]+?)(?:;|$)'
    # remove ignored 
    inp = re.sub(ignorePat, ';', inp).strip(';')
    # only split if ; not in within quotes ('') 
    splitPat = r';(?=(?:[^\'"]*\'[^\'"]*\')*[^\'"]*$)'
    infArgs = re.split(splitPat, inp)
    # remove single quotes
    for arg in infArgs:
        arg = arg.replace("'",'')
        args.append(arg)
    return args


# return [binary executable path, arguments+]
def getCmdList(arg):
    cmdList = arg.split()
    if not cmdList:
        return None
    cmd = cmdList[0].lower()
    path = findPath(cmd)
    if path:
        commandList = [path] + cmdList[1:]
    else:
        print(f"fash: {cmd}: command not found")
        return None
    return commandList


# process each command and its arguements 
def processCmd(arg):
    global quitCmd
    global background_pids
    cmdList = arg.split()
    cmd = cmdList[0].lower()
    # leave when requested
    if cmd=='quit':
        if(handleQuit()):
            quitCmd = True
            return
    # change directories
    elif cmd=='cd':
        handleCd(cmdList)
    else:
    # regular command requests
        cidx = None
        filename = None
        flags = None
        mode = None
        # redirection checking
        if '<' in arg:
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
        # if command exists 
        commandList = getCmdList(arg)
        if commandList:
            # redirection handling
            if filename:
                handleRedirect(commandList, filename, mode, flags)
            else:
                # background and foreground process management
                pType = "bg" if arg.endswith('&') else "fg"
                pid = runProcess(commandList)
                if pType == "bg":
                    background_pids.append(pid)
                elif pType == "fg":
                    # wait if a foreground process
                    pid, status = os.waitpid(pid, 0)
                    # alert if failed
                    if not os.WIFEXITED(status):
                        print(f"Program terminated: exit code {status}.")
                        sys.exit(1)
  
    
# handle piping between commands
def handlePipes(prevCmd, currCmd):
    # get command lists
    prevCmd=getCmdList(prevCmd)
    currCmd=getCmdList(currCmd)
    try:
        # open communication
        r, w = os.pipe()   # read, write
        cpid1 = os.fork()
        if cpid1 == 0:
            # child process one
            os.dup2(w, 1) # redirect std output to the write end of pipe
            os.close(r)
            os.close(w)
            os.execv(prevCmd[0], prevCmd)
        elif cpid1 > 0:
            # parent process, close write end
            os.close(w)
            cpid2 = os.fork()
            if cpid2 == 0:
                # second child 
                os.dup2(r, 0) # redirect std input to the read end of pipe
                os.close(r)
                os.execv(currCmd[0], currCmd)
            elif cpid2 > 0:
                # parent process, close read end
                os.close(r)
                # wait for children to finish, return if failed
                pid, stat1 = os.waitpid(cpid1, 0)
                pid, stat2 = os.waitpid(cpid2, 0)
                if not os.WIFEXITED(stat1):
                    return os.WEXITSTATUS(stat1)
                if not os.WIFEXITED(stat2):
                    return os.WEXITSTATUS(stat2)
                return None
    except Exception as e:
        print(f"Error: {e}")


# handle if exit request
def handleQuit():
    # background process need cleaning
    if background_pids:
        print("There are background processes running.")
        inp = input("Are you sure you want to exit when there are processes running in the background? (y/n) ").strip()
        if inp == "n":
            return False
        elif inp == "y":
            # wait for bg processes to finish
            for pid in background_pids:
                os.waitpid(pid, 0)
    print("Exiting...")
    return True
    

# handle directory changes
def handleCd(cmdList):
    global ps1
    if len(cmdList) > 1:
        try:
            # attempt to change directory
            os.chdir(cmdList[1])
        except (NotADirectoryError, FileNotFoundError, PermissionError) as e:
            print(f"fash: cd: {cmdList[1]}: {str(e)}")
    else:
        # cd -> home
        os.chdir(os.environ.get('HOME'))
    # keep prompt up to date
    ps1 = os.getcwd() + ' $ '


# handle each argument involved in a pipe
def parsePipes(arg):
    prev = re.split(r'\s*\|\s*', arg)
    idx = 0
    prevCmd = None
    # iterate through each command
    while(prev):
        if(idx==0):
            # first doesn't depend on a prev
            processCmd(prev[0])
        else:
            handlePipes(prevCmd, prev[0])
        # get prev from head of list
        prevCmd = prev.pop(0)
        idx+=1


# handle user input
def handleInput(inp):
    inp = inp.strip()
    # reset if nothing given
    if not inp:
        return
    args = getArgs(inp)
    for arg in args:
        # pipe check
        if '|' in arg:
            parsePipes(arg)
        else:
            # process non-piped commands
            processCmd(arg)


# main handler
def main():
    try:
        while (1):
            # prompt user until exited
            handleInput(input(ps1))
            if quitCmd:
                break
    except KeyboardInterrupt:
        print("\nExited on KeyboardInterrupt")
        sys.exit(0)
        
        
if __name__ == "__main__":
    main()