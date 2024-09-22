import os
import cmd


# generate redirection parameters
def handle_redirection(command):
    input_file = None
    output_file = None
    # input redirection
    if '<' in command:
        parts = command.split('<')
        command = parts[0].strip()
        if not command:
            command = parts[-1].split()[-1]
        input_file = ''.join(parts[1]).split()[0].strip()
        
    # output redirection
    if '>' in command:
        parts = command.split('>')
        command = parts[0].strip()
        if not command:
            command = parts[-1].split()[-1]
        output_file = ''.join(parts[1]).split()[0].strip()
    command_lst = cmd.get_cmd_lst(command)
    return command_lst, input_file, output_file


# set file descriptors to redirect io
def redirect_io(input_file, output_file):

    # input redirection
    if input_file:
        infile = os.open(input_file, os.O_RDONLY)
        os.dup2(infile, 0)  # redirect std input from input file
        os.close(infile)

    # output redirection
    if output_file:
        outfile = os.open(output_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        os.dup2(outfile, 1)  # redirect std output to output file
        os.close(outfile)
    
    

