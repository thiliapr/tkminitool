import argparse
import datetime
import subprocess
import time
from typing import Any

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


def get_trace_info() -> dict[str, Any] | Exception:
    try:
        r = requests.get("https://one.one.one.one/cdn-cgi/trace", timeout=5)
    except ConnectionError as e:
        return e

    info = dict([kv.split("=", 2) for kv in r.text.splitlines()])
    return info


def time_strf():
    return datetime.datetime.now().strftime("[%Y-%m-%d] [%H:%M:%S]")


def main():
    parser = argparse.ArgumentParser(
        prog='warp-colo-chooser',
        description='Choose the colo of warp to target',
        epilog='Copyright By thiliapr, License by GPLv3.')
    parser.add_argument("--pause", action="store_true", help="The program will pause before exit.")
    parser.add_argument("--only-ipv4", action="store_true", default=True, help="The program will stop when IP is IPv4.")
    parser.add_argument("--only-ipv6", action="store_true", help="The program will stop when IP is IPv6.")
    parser.add_argument("-c", "--colo", type=str, default="HKG", help="The program will setting colo to this.")
    parser.add_argument("-p", "--warp-cli-path", type=str, default="C:\\Program Files\\Cloudflare\\Cloudflare WARP",
                        help="Path of CLI of Cloudflare")
    args = parser.parse_args()

    while True:
        print(time_strf(), "Try to reconnect...")
        warp_reconnect(args.warp_cli_path)
        print(time_strf(), "Reconnected.")

        trace_info = get_trace_info()

        if isinstance(trace_info, Exception):
            print("Conncetion Error:", trace_info.strerror)
            break

        print(time_strf(), "Info:", "IP=" + trace_info["ip"], "colo=" + trace_info["colo"])

        if args.only_ipv4:
            if "." not in trace_info["ip"]:
                break
        elif args.only_ipv6:
            if "[" not in trace_info["ip"]:
                break

        if trace_info["colo"] == args.colo:
            print("Congratulations! You have successfully switched colo to {}.".format(args.colo), flush=True)
            break

    if args.pause:
        input("Enter to exit: ")


if __name__ == "__main__":
    main()
