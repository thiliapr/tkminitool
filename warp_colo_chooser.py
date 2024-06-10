import argparse
import datetime
import subprocess
import time

import requests

"""
Requirements:
requests
"""

def get_program_output(args):
    try:
        output = subprocess.check_output(args, universal_newlines=True)
        return output
    except subprocess.CalledProcessError:
        return ""


def warp_reconnect(warp_cli_path):
    subprocess.check_output(["{}/warp-cli".format(warp_cli_path), "disconnect"], universal_newlines=True)
    while "Disconnected" not in get_program_output(["{}/warp-cli".format(warp_cli_path), "status"]):
        time.sleep(1)

    subprocess.check_output(["{}/warp-cli".format(warp_cli_path), "connect"], universal_newlines=True)
    while "Connected" not in get_program_output(["{}/warp-cli".format(warp_cli_path), "status"]):
        time.sleep(1)


def get_colo():
    r = requests.get("https://one.one.one.one/cdn-cgi/trace")

    colo_loc = r.text.find("colo=")
    colo = r.text[colo_loc + 5:colo_loc + 8]

    return colo


def main():
    parser = argparse.ArgumentParser(
        prog='warp-colo-chooser',
        description='Choose the colo of warp to target',
        epilog='Copyright By thiliapr, License by GPLv3.')
    parser.add_argument("-c", "--colo", type=str, default="HKG", help="The program will setting colo to this.")
    parser.add_argument("-p", "--warp-cli-path", type=str, default="C:\\Program Files\\Cloudflare\\Cloudflare WARP",
                        help="Path of CLI of Cloudflare")
    args = parser.parse_args()

    while True:
        print(datetime.datetime.now().strftime("[%Y-%m-%d] [%H:%M:%S]"), "Try to reconect..."
        warp_reconnect(args.warp_cli_path)

        cur_colo = get_colo()
        print("{} Switched colo to {}.".format(datetime.datetime.now().strftime("[%Y-%m-%d] [%H:%M:%S]"), cur_colo), flush=True)

        if cur_colo == args.colo:
            print("Congratulations! You have successfully switched colo to {}.".format(args.colo), flush=True)
            return


if __name__ == "__main__":
    main()
