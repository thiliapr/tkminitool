import pathlib
import json


def main():
    for novel_path in pathlib.Path("novel").glob("*"):
        if not novel_path.is_dir():
            continue
        for chapter_path in novel_path.glob("*.txt"):
            print(chapter_path)
            with open(chapter_path, "r", encoding="utf-8") as cf, \
                    open(chapter_path.parent / (chapter_path.name.removesuffix(".txt") + ".json"), "w", encoding="utf-8") as pf:
                json.dump([{"message": line.strip()} for line in cf.readlines() if line.strip()], pf, indent="\t", ensure_ascii=False)


if __name__ == '__main__':
    main()
