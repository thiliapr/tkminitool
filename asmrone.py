import requests
import json
import os
import argparse
import platform
import shutil
import subprocess
import sys


def read_asmrone(path: dict, cur_path: str, files: list[tuple[str, str]] | None = None) -> list[tuple[str, str]]:
    if files is None:
        files = []

    if path["type"] == "folder":
        for file in path["children"]:
            read_asmrone(file, os.path.join(cur_path, path["title"]), files)
    else:
        files.append((cur_path, path["title"], path["mediaDownloadUrl"]))

    return files


def clear() -> None:
    if platform.system() == "Linux":
        os.system("clear")
    elif platform.system() == "Windows":
        os.system("cls")
    else:
        print("\n" * 20)


def ask_which_remove(files: list) -> None:
    while True:
        clear()

        # Show files
        for i in range(len(files)):
            print(f"{i})", files[i][0], files[i][1])

        # Get which remove
        answer = input("Which would you remove (e.g `0, 1-2`, enter to download, q to quit): ")

        # If quit
        if answer == "q":
            sys.exit()
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
    parser.add_argument("-m", "--mirror", type=str, help="Download Mirror", default="asmr.one", required=False, dest="host")
    args = parser.parse_args()

    # No RJ number in Arguments
    rj = args.rj
    if rj is None:
        rj = input("RJ: ")

    # Delete "RJ" in string
    rj = int(rj[rj.startswith("RJ") * 2:])

    # Request directory from amsr.one
    directory_content = json.loads(requests.get(f"https://api.{args.host}/api/tracks/{rj}").content)
    directory = {"type": "folder", "title": f"RJ{rj}", "children": directory_content}

    # Read directory
    files = read_asmrone(directory, "")

    # Which don't like
    ask_which_remove(files)

    # Download
    curl = shutil.which("curl")
    assert curl, "curl not found."

    for file in files:
        path, filename, url = file
        filepath = os.path.join(path, filename)

        if os.path.isfile(path):
            os.remove(path)
        if not os.path.exists(path):
            os.system(f'mkdir "{path}"')

        print(f"Donwload {filepath}")
        curl_process = subprocess.Popen((curl, url, "-C", "-", "-o", filepath))
        curl_process.wait()


if __name__ == '__main__':
    main()
