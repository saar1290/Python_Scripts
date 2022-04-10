import re
import subprocess
from colorama import Fore, Style


ip = input(Fore.LIGHTBLUE_EX+"Please enter an IP address belonging to the netstick: "+Style.RESET_ALL)
dname = "soifield"
file = open('/etc/hosts', 'r+')
lines = file.readlines()
reg = re.compile(fr"^[0-9].* {dname}")

for index, line in enumerate(lines):
    match = reg.match(line)
    if match is not None:
        old = lines[index]
        lines.remove(old)
        lines.insert(index, f"{ip} {dname}"+"\n")
        file.seek(0)
        file.truncate()
        file.writelines(lines)
        file.close()
        print(Fore.LIGHTGREEN_EX+f"{dname} IP address changed to {ip}"+Style.RESET_ALL)
        subprocess.call(['ping', f"{dname}", '-c', '3'])
        