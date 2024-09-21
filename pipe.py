import os
import re
import cmd


# handle each argument involved in a pipe
def parse(arg):
    prev = re.split(r'\s*\|\s*', arg)
    idx = 0
    prev_cmd = None
    while(prev):                # iterate through each command
        if(idx!=0):
            handler(prev_cmd, prev[0])
        prev_cmd = prev.pop(0)  # get prev from head of list
        idx+=1
        
        
import os

def handler(prev_cmd, curr_cmd):
    # get command lists
    prev_cmd = cmd.get_cmd_lst(prev_cmd)
    curr_cmd = cmd.get_cmd_lst(curr_cmd)
    try:
        r, w = os.pipe()    # open communication: read, write
        cpid1 = os.fork()   # create first child process
        if cpid1 == 0:
            os.dup2(w, 1)   # redirect stdout to write end of pipe
            os.close(r)
            os.execv(prev_cmd[0], prev_cmd)
        else:
            os.close(w)  # close write end in parent
            cpid2 = os.fork()  # create second child process
            if cpid2 == 0:
                os.dup2(r, 0)   # redirect stdin to read end of pipe
                os.close(r)
                os.execv(curr_cmd[0], curr_cmd)
            else:
                os.close(r)  # close read end in parent
        # wait for children
        pid1, stat1 = os.waitpid(cpid1, 0)
        pid2, stat2 = os.waitpid(cpid2, 0)

        # check exit status
        if os.WIFEXITED(stat1) and os.WEXITSTATUS(stat1) != 0:
            return os.WEXITSTATUS(stat1)
        if os.WIFEXITED(stat2) and os.WEXITSTATUS(stat2) != 0:
            return os.WEXITSTATUS(stat2)

    except Exception as e:
        print(f"Error: {e}")
        return -1

