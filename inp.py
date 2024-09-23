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
            pipe.handler(arg)
        else:            # process non-piped commands
            cmd.process_cmd(arg)


# create list of args from inp
def get_args(inp):
    args = []
    in_quotes = False
    current_arg = []
    for char in inp:
        if char in '"\'':
            in_quotes = not in_quotes # toggle in_quotes state
        elif char == '#':
            if not in_quotes:         # ignore everything after hash
                break
        elif char == ';':             # command seperator
            if not in_quotes:
                args.append(''.join(current_arg).strip())  # add arg
                current_arg = []                           # reset word list once end
                continue                                   # continue getting every character within command
        current_arg.append(char)  # add chars to total arg
    # add last arg if needed
    if current_arg:
        args.append(''.join(current_arg).strip())
    return args
