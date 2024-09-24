#!/usr/bin/env python3

import cmd
import inp
import sys

# main handler
def main():
    if len(sys.argv) > 1:  # file is specified
        f = sys.argv[1]
        try:
            with open(f, 'r') as file:
                for line in file:
                    line = line.strip()
                    try:
                        inp.handler(line)    # execute the command
                        if cmd.quit_cmd:
                            break
                    except Exception as e:
                        print(f"Error executing '{line}': {e}")
        except FileNotFoundError as e:
            print(f"Fash: {e}")
    else:
        try:
            while True:
                inp.handler(input(cmd.ps1))  # prompt user until exited
                if cmd.quit_cmd:
                    break
        except KeyboardInterrupt:
            print("\nExited on KeyboardInterrupt")
            return 1

if __name__ == "__main__":
    main()

