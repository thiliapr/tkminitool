import os
import subprocess
import shutil
import threading
import sys
from typing import Any, Callable

playing_process = None
devnull = open(os.devnull, 'w')


def play(path: str, recursion_depth: int = 0):
    global playing_process

    if os.path.isdir(path):
        for p1 in os.listdir(path):
            play(os.path.join(path, p1), recursion_depth + 1)
    else:
        print(path, end="", flush=True)

        playing_process = subprocess.Popen((shutil.which("ffplay"), "-nodisp", "-autoexit", path), stderr=devnull, stdout=devnull)
        if playing_process.wait() == 0:
            print()


def loop(func: Callable, args: list, kwargs: dict):
    while 1:
        func(*args, **kwargs)


def main():
    # Check
    assert shutil.which("ffplay"), "ffplay failed. code: 404"

    # Start
    global playing_process
    threading.Thread(target=loop, args=(play, (os.getcwd(),), {}), daemon=True).start()

    try:
        while True:
            sys.stdin.readline()
            playing_process.kill()
    except KeyboardInterrupt:
        playing_process.kill()


if __name__ == '__main__':
    main()
