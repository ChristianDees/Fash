import os

# handle i/o redirection
def handler(cmd, filename, mode, flags):
    try:
        pid = os.fork()
        # child process
        if pid == 0:
            # get file descriptor
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
                rc = os.WEXITSTATUS(status)
                if rc != 0:
                    # return exit code if failed
                    return rc
    except Exception as e:
        print(f"Error: {e}")
        return 1
