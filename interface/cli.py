#!/usr/bin/env python3
from iskra.engine import run_step
def main():
    print("Искра REPL — :q выйти")
    who = "iskra_core"
    while True:
        try:
            line = input(f"{who}> ")
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip() == ":q":
            break
        print(run_step(who, line))
if __name__ == "__main__":
    main()
