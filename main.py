import cmd
import inp
import sys


# main handler
def main():
    if len(sys.argv) > 1:              # file is specified
        file = sys.argv[1]
        try:
            f = open(file,'r')
            for line in f:
                inp.handler(line)      # run each line as command
                if cmd.quit_cmd:
                    break
        except FileNotFoundError:
            print(f"File {file} not found.")
    try:
        while (1):
            inp.handler(input(cmd.ps1)) # prompt user until exited
            if cmd.quit_cmd:
                break
    except KeyboardInterrupt:
        print("\nExited on KeyboardInterrupt")
        return 1
        
        
if __name__ == "__main__":
    main()
