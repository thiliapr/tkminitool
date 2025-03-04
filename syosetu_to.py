import pathlib
import json
import os


def main():
    for novel_path in pathlib.Path("novel").glob("*"):
        if not novel_path.is_dir():
            continue
        for chapter_path in novel_path.glob("*.txt"):
            trans_path = pathlib.Path("trans") / novel_path.name / (chapter_path.name.removesuffix("txt") + "json")
            if not trans_path.exists():
                print("del", chapter_path)
                os.remove(chapter_path)
                continue
            print(chapter_path)
            with open(chapter_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(trans_path, "r", encoding="utf-8") as f:
                for msg in json.load(f):
                    content = content.replace(msg["source"], msg["translation"])
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(content)


if __name__ == '__main__':
    main()
