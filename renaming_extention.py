from pathlib import Path
import argparse
import sys
from colorama import Fore, Style

parser = argparse.ArgumentParser(description='Renaming files extension')
parser.add_argument('--path', dest='path', type=str, help='Parent path of subdirectories')
parser.add_argument('--current-ext', dest='current_extension', type=str, help='Current files extension with')
parser.add_argument('--desirable-ext', dest='desirable_extension', type=str, help='Desirable files extension with')
if len(sys.argv) < 7:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
path = args.path
current_extension = args.current_extension
desirable_extension = args.desirable_extension

def rename(path,current_extension,desirable_extension):
    list = sorted(Path(path).glob(f'**/*.{current_extension}'))
    test_list = sorted(Path(path).glob(f'**/*.{desirable_extension}'))
    print(Fore.LIGHTYELLOW_EX + "Path:" + Style.RESET_ALL + Fore.LIGHTCYAN_EX + f" {path}" + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "The Current_extension:" + Style.RESET_ALL + Fore.LIGHTCYAN_EX + f" {current_extension}" + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "The Desirable_extension:" + Style.RESET_ALL + Fore.LIGHTCYAN_EX + f" {desirable_extension}" + Style.RESET_ALL)

    for file in test_list:
        file = str(file)
        if desirable_extension in file:
            print(Fore.LIGHTRED_EX+f"The Deirable extension is already belongs to {file}")
            
    for file in list:
        file.rename(file.with_suffix('.'+desirable_extension))
        print(Fore.LIGHTGREEN_EX+f"File {file} is renamed to extension to {desirable_extension}..."+Style.RESET_ALL)

rename(path, current_extension, desirable_extension)
