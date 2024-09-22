import os
import cmd


# generate redirection parameters
def handle_redirection(cmd):
    input_file = None
    output_file = None
    # input redirection
    if '<' in cmd:
        parts = cmd.split('<')
        cmd = parts[0].strip()
        if not cmd:
            cmd = parts[-1].split()[-1]
        input_file = ''.join(parts[1]).split()[0].strip()
        
    # output redirection
    if '>' in v:
        parts = cmd.split('>')
        cmd = parts[0].strip()
        if not cmd:
            cmd = parts[-1].split()[-1]
        output_file = ''.join(parts[1]).split()[0].strip()
    cmd_lst = cmd.get_cmd_lst(cmd)
    return cmd_lst, input_file, output_file


# set file descriptors to redirect io
def redirect_io(input_file, output_file):

    # input redirection
    if input_file:
        in_fd = os.open(input_file, os.O_RDONLY)
        os.dup2(in_fd, 0)   # redirect std input from input file
        os.close(in_fd)

    # output redirection
    if output_file:
        out_fd = os.open(output_file, os.O_WRONLY | os.O_CREAT)
        os.dup2(out_fd, 1)  # redirect std output to output file
        os.close(out_fd)
    
    

