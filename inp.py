import re
import cmd
import pipe

# handle user input
def handler(inp):
    inp = inp.strip()
    if not inp:         # reset if nothing given
        return
    args = get_args(inp)
    for arg in args:
        if '|' in arg:   # pipe check
            pipe.parse(arg)
        else:            # process non-piped commands
            cmd.process_cmd(arg)

# create list of args from inp
def get_args(inp):
    # remove comments, but not ones within quotes
    pattern = r'(?<!["\'])#(?![^"\']*["\'])'
    inp = re.sub(pattern, '', inp)
    # split by semicolon not within quotes and clean up
    args = [arg.strip() for arg in re.split(r';(?=(?:[^\'"]*\'[^\'"]*\')*[^\'"]*$)', inp) if arg.strip()]
    return args
