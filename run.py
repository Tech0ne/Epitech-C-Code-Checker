#!/usr/bin/python3

######################
##   ___           
##  | _ \_  _ _ _  
##  |   / || | ' \ 
##  |_|_\\_,_|_||_|
##                 
######################

from rich import print

from rich.panel import Panel
from rich.align import Align
from rich.table import Table

from subprocess import run

import sys
import os

print(Panel(Align("""[blue]   ___ ___ _           _       
  / __/ __| |_  ___ __| |__ ___
 | (_| (__| ' \/ -_) _| / /(_-<
  \___\___|_||_\___\__|_\_\/__/""", align="center"), border_style="green"))

args = ' '.join(sys.argv[1:])
if not args:
    args = None

display = '"' + args + '"' if args is not None else args

print(Panel(f"[red]Using arguments : {display}", border_style="green"))

def error(message: str, code: int) -> None:
    print(Panel(Align(message, align="center"), border_style="red"))
    os.system("make -C /app/ fclean >/dev/null 2>/dev/null")
    sys.exit(code)

######## Compilations ########
print(Panel(Align("[bold]Starting multiple compilations", align="center"), border_style="green"))

if not os.path.isfile("/app/Makefile"):
    error("No Makefile !", 1)

with open("/app/Makefile", 'r') as f:
    data = f.read().split('\n')

name = flags = ""
for line in data:
    if line.startswith("NAME"):
        name = line.split('=')[-1].replace(' ', '').replace('\t', '')

for line in data:
    if line.startswith("CFLAGS") or line.startswith("FLAGS"):
        flags += line.split('=')[-1].replace("$", "\\$")

if name == "":
    error("How comes you dont have a \"NAME\" variable on your Makefile ???")

print(Panel(f"Using filename : \"{name}\"", border_style="green"))

## Normal
print(Panel("Normal compilation", border_style="green"))
err_code = os.system("make -C /app/")
if err_code != 0:
    error(f"Somthing went wrong with a sample make (error code {err_code}) !", err_code)
if not os.path.isfile(f"/app/{name}"):
    error("Compiled file not found !", 1)

input("\nPress enter")

## fclean
print(Panel("Sample fclean", border_style="green"))
err_code = os.system("make -C /app/ fclean")
if err_code != 0:
    error(f"Something went wrong with a sample make fclean (error code {err_code}) !", err_code)
if os.path.isfile(f"/app/{name}"):
    error(f"File /app/{name} still there, wtf is your fclean doing ???", 1)

input("\nPress enter")

## debug
print(Panel("Debug compilaton (shows warnings)", border_style="green"))
err_code = os.system(f"make -C /app/ FLAGS=\"{flags} -Wall -Wextra -g3\" CFLAGS=\"\\$(FLAGS)\"")
if err_code != 0:
    error(f"Somthing went wrong when compiling with debug flags (error code {err_code}) !", err_code)
if not os.path.isfile(f"/app/{name}"):
    error("Compiled file not found !")

input("\nPress enter")

print(Panel(Align("[bold]Compilations tests done", align="center"), border_style="green"))

######## Checks ########
print(Panel(Align("[bold]Starting binary tests", align="center"), border_style="green"))

file = f"/app/{name}"

## gdb listing
print(Panel("GDB syscall listing", border_style="green"))

os.system(f"gdb '{file}' -ex 'source /opt/gdbscript.py' -ex 'quit' > /dev/null")
with open("/tmp/function_list.result", 'r') as f:
    syscall_list = f.read().split('\n')

while '' in syscall_list:
    syscall_list.remove('')

table = Table(title="Syscall listing :", expand=True)

for syscall in syscall_list:
    s = syscall.replace("@plt", "[gray23]@plt[/]")
    if not "@plt" in s and s.split(' ')[-1].startswith('_'):
        s = "[gray23]" + s + "[/]"
    else:
        if "@plt" in s:
            s = "[blue]" + s
        else:
            s = "[red]" + s
    table.add_row(s)

print(Panel(table))

input("\nPress enter")

## objdump
print(Panel("Objdump output", border_style="green"))

print(Panel(run(["objdump", "-d", file], check=False, capture_output=True).stdout.decode(), title="[green]Objdump output", title_align="left"))

input("\nPress enter")

## hexyl
print(Panel("Hex view of the program", border_style="green"))

os.system(f"hexyl {file}")

input("\nPress enter")

## file size
print(Panel("File size of the program", border_style="green"))

print(Panel(run(["du", "-sh", file], check=False, capture_output=True).stdout.decode(), title="File size", title_align="left"))

input("\nPress enter")

######## Run checks ########
print(Panel(Align("[bold]Starting runing scans")))

print(Panel("Testing \"-h\" and \"--help\"", border_style="green"))

err_code = os.system(f"{file} -h")
print(Panel(f"Throws error code {err_code} with \"-h\""))

err_code = os.system(f"{file} --help")
print(Panel(f"Throws error code {err_code} with \"--help\""))

input("\nPress enter")

print(Panel("Testing normal run", border_style="green"))

err_code = os.system(f"{file} {args if args is not None else ''}")
if err_code != 0:
    print(Panel(f"[dark_orange3]Normal run throws error code {err_code}"))

input("\nPress enter")

print(Panel("Testing valgrind", border_style="green"))

valg = run(["valgrind", file] + sys.argv[1:], check=False, capture_output=True).stderr.decode()
print(Panel(valg))
color = ''
text = ''
if "no leaks are possible" in valg:
    color = "green"
    text = "No data loss found"
if "definitely lost: 0 bytes" in valg:
    color = "dark_orange3"
    text = "Seems that there are data loss, but unusual ones"
if color == '':
    color = "red"
    text = "Your program does leak data.\nFix this issue before coming back"

print(Panel(text, border_style=color))

if color != "green":
    print(Panel("Running valgrind again with \"--leak-check=full\""))
    print(Panel(run(["valgrind", "--leak-check=full", file] + sys.argv[1:], check=False, capture_output=True).stderr.decode()))

if color == "red":
    error("This test will not continue", 666)

input("\nPress enter")

print(Panel("Running strace", border_style="green"))

strace = run(["strace", file] + sys.argv[1:], check=False, capture_output=True).stderr.decode()
print(Panel(strace, title="STrace output", title_align="left"))

os.system("make -C /app/ fclean >/dev/null 2>/dev/null")

input("\nPress enter")

print(Panel(Align("[red]Tests over", align="center"), border_style="green"))
