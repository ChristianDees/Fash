import os
import cmd

append = False

# generate redirection parameters
def handler(inp_cmd):
    input_file = None
    output_file = None
    global append
    command = inp_cmd
    # input redirection
    if '<' in inp_cmd or '<<' in inp_cmd:
        parts = inp_cmd.split('<')
        command = parts[0].strip()
        if not command:
            command = parts[-1].split()[-1]
        input_file = ''.join(parts[1]).split()[0].strip()
        
    # output redirection
    if '>' in inp_cmd:
        if '>>' in inp_cmd:
            parts = inp_cmd.split('>>')
            append = True
        else:
            parts = inp_cmd.split('>')
        command = parts[0].strip()
        if not command:
            command = parts[-1].split()[-1]
        output_file = ''.join(parts[1]).split()[0].strip()
    cmd_lst = cmd.get_cmd_lst(command)
    return cmd_lst, input_file, output_file


# set file descriptors to redirect io
def redirect_io(input_file, output_file):
    global append
    flags = None
    # input redirection
    if input_file:
        flags = os.O_RDONLY
        in_fd = os.open(input_file, flags)
        os.dup2(in_fd, 0)   # redirect std input from input file
        os.close(in_fd)

    # output redirection
    if output_file:
        flags = os.O_WRONLY | os.O_CREAT
        if append:
            flags |= os.O_APPEND
        out_fd = os.open(output_file, flags)
        os.dup2(out_fd, 1)  # redirect std output to output file
        os.close(out_fd)

