import os


def vtt2lrc(vttc: str):
    lines = vttc.splitlines()
    if lines[0] == "WEBVTT":
        lines = lines[1:]

    vtts: list[tuple[str, str, str]] = [lines[i * 4:(i * 4) + 4] for i in range(int(len(lines) / 4))]
    lrcs: list[str] = []

    for vtt in vtts:
        start, end = vtt[2].split(" --> ", 2)
        msg = vtt[3]

        lrcs.append(f"[{start[3:]}]{msg}")

    return "\n".join(lrcs)


def main():
    for f in os.listdir():
        if not f.endswith(".vtt"):
            continue

        with open(f, encoding="utf-8") as fp:
            flrc = vtt2lrc(fp.read())
        with open(f.removesuffix(".vtt") + ".lrc", encoding="cp936", mode="w") as fp:
            fp.write(flrc)


if __name__ == '__main__':
    main()
