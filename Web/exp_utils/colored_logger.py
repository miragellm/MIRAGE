import os
import sys
from rich.console import Console

class ColoredLogger(object):
    def __init__(self, args):
        # make log folder
        folder_name = args.result_dir
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
                
        # make log_file
        self.log_file = f"{args.result_dir}/{args.log_name}.txt"
        open(self.log_file, 'w')

        # set console
        self.console = Console()

    def _print(self, text, option):
        if option == "console":
            self.console.print(text)
        elif option == "print":
            print(text)
        else:
            raise ValueError("Invalid option")

    def log(self, *args, option="print"):
        text = ' '.join([str(arg) for arg in args])
        default_stdout = sys.stdout  # assign console output to a variable
        self._print(text, option=option)
        f = open(self.log_file, 'a')
        sys.stdout = f
        self._print(text, option=option)
        sys.stdout = default_stdout  # set stdout back to console output