import os
import re
import redirect

def handler(arg):
    cmds = arg.split('|')
        
    # get pipes for each command (exclude last)
    pipes = []
    for i in range(len(cmds) - 1):
        r, w = os.pipe()
        pipes.append((r, w))
        
    for idx, cmd in enumerate(cmds):
        cmd_lst, input_file, output_file = redirect.handle_redirection(cmd)
        try:
            pid = os.fork()
            if pid == 0:
                if input_file or output_file:
                    redirect.redirect_io(input_file, output_file)
                # if command isn't first...
                if idx != 0:
                    os.dup2(pipes[idx-1][0], 0)     # duplicate read end of prev pipe to std input
                                                    # now this cmd will read from output of prev cmd
                # if cmd isn't last...
                if idx != len(cmds) - 1:
                    os.dup2(pipes[idx][1], 1)       # duplicate write end of current pipe to std ouput
                                                    # now this cmds output will send to next cmd
                # close all child process pipes (they were inherited from parent)
                for r, w in pipes:
                    os.close(r)
                    os.close(w)
                try:
                    os.execv(cmd_lst[0], cmd_lst)   # execute the command
                except FileNotFoundError:
                    print(f"Command not found: {cmd[0]}")
                    sys.exit(1)
        except Exception as e:
            print(f"Error executing process: {e}")
        
    # close all parent pipes
    for r, w in pipes:
        os.close(r)
        os.close(w)
        
    # wait for all child processes to finish
    for cmd in cmds:
        pid, status = os.wait()
        if not os.WIFEXITED(status):
            print(f"Program terminated with exit code {os.WEXITSTATUS(status)}.")
