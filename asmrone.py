import requests
import argparse
import platform
import re
from os import makedirs
from subprocess import Popen, run
from sys import exit
from shutil import which
from pathlib import Path

"""
requirements:
requests
"""


def read_asmrone(file: dict, cur_path: Path, files: list[tuple[str, str]] | None = None) -> list[tuple[Path, str]]:
    if files is None:
        files = []

    cur_path = cur_path.parent / re.sub(r'[<>:"/\\|?*]', '_', cur_path.name).replace("\n", "")
    print(cur_path)

    if file["type"] == "folder":
        for child in file["children"]:
            read_asmrone(child, cur_path / child["title"], files)
    else:
        files.append((cur_path, file["mediaDownloadUrl"]))

    return files


def clear() -> None:
    if platform.system() == "Linux":
        run("clear", shell=True)
    elif platform.system() == "Windows":
        run("cls", shell=True)
    else:
        print("\n" * 20)


def ask_which_remove(files: list) -> None:
    while True:
        clear()

        # Show files
        for i in range(len(files)):
            print(f"{i})", files[i][0])

        # Get which remove
        answer = input("Which would you remove (e.g `0, 1-2`, enter to download, q to quit): ")

        # If quit
        if answer == "q":
            exit()
        elif answer == "":
            break

        # Get remove_start_at, number_to_remove
        if answer.find("-") == -1:
            remove_start_at = int(answer)
            number_to_remove = 1
        else:
            r = [int(at) for at in answer.split("-", 2)]
            remove_start_at = r[0]
            number_to_remove = r[1] - r[0] + 1
            del r

        # Pop
        for _ in range(number_to_remove):
            files.pop(remove_start_at)
    clear()


def main():
    parser = argparse.ArgumentParser(
        prog="asmrone",
        description="Download AMSR From amsr.one",
        epilog="License: MIT License"
    )
    parser.add_argument("-r", "--rj-number", type=str, help="Format: RJXXXXX", dest="rj")
    parser.add_argument("-m", "--mirror", type=str, help="Download Mirror", default="asmr-200.com", required=False, dest="host")
    parser.add_argument("-p", "--proxy", type=str, help="Proxy", required=False, dest="proxy")
    args = parser.parse_args()

    # No RJ number in Arguments
    rj = args.rj
    if rj is None:
        rj = input("RJ: ")

    # Delete "RJ" in string
    rj = int(rj[rj.startswith("RJ") * 2:])

    # Get Info
    info = requests.get(f"https://api.{args.host}/api/workInfo/{rj}", proxies={"https": args.proxy} if args.proxy else {}).json()

    # Request directory from amsr.one
    directory_content = requests.get(f"https://api.{args.host}/api/tracks/{info['id']}?v=1", proxies={"https": args.proxy} if args.proxy else {}).json()
    directory = {"type": "folder", "title": f"RJ{rj}", "children": directory_content}

    # Read directory
    files = read_asmrone(directory, Path(""))

    # Which don't like
    ask_which_remove(files)

    # Download
    curl = which("curl")
    assert curl, "curl not found."

    for file in files:
        filepath, url = file
        filepath = f"RJ{rj}" / filepath
        print(f"url: {url}")
        print(f"path: {filepath}")
        makedirs(filepath.parent, exist_ok=True)
        curl_process = Popen((curl, f'{url}', "--progress-bar", "--continue-at", "-", "-o", f'{filepath}') + (("-x", args.proxy) if args.proxy else ()))
        curl_process.wait()


if __name__ == '__main__':
    main()
