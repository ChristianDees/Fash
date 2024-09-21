import cmd
import inp

# main handler
def main():
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
