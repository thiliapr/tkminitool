import os
import argparse
import requests
from bs4 import BeautifulSoup


def fetch_page_content(url, proxy=None):
    """请求页面内容并返回解析后的BeautifulSoup对象"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
    }
    proxies = {"https": proxy} if proxy else {}

    try:
        response = requests.get(url, proxies=proxies, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是200，会抛出异常
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None


def fetch_chapters(novel_id, page, proxy=None):
    """获取指定小说页的章节列表"""
    url = f"https://ncode.syosetu.com/{novel_id}/?p={page}"
    soup = fetch_page_content(url, proxy)

    if soup is None:
        return [], None, None

    # 获取小说标题
    novel_title = soup.select_one(".p-novel__title").text.strip()

    # 获取章节列表
    chapters = []
    for sublist in soup.select(".p-eplist__sublist"):
        subtitle = sublist.select_one(".p-eplist__subtitle")
        chapters.append((subtitle.text.strip(), subtitle.get("href")))

    # 检查是否有下一页
    next_button = soup.select_one(".c-pager__item--next")
    next_page_url = next_button.get("href") if next_button else None

    return chapters, novel_title, next_page_url


def fetch_chapter_content(chapter_url, proxy=None):
    """获取单个章节的内容"""
    soup = fetch_page_content(chapter_url, proxy)

    if soup is None:
        return ""

    document = soup.select_one(".p-novel__text")
    paragraphs = [p.text.strip() for p in document.select("p")]

    return "\n".join(paragraphs)


def save_chapters_to_file(novel_title, chapters, proxy=None):
    """将章节内容保存到文件中"""
    # 创建目录
    os.makedirs(f"novel/{novel_title}", exist_ok=True)

    for title, href in chapters:
        filename = title.replace("/", "／").replace("\"", "")
        chapter_file = f"novel/{novel_title}/{filename}.txt"
        if os.path.exists(chapter_file):
            continue

        print(f"正在获取章节：{title} ...")
        chapter_url = f"https://ncode.syosetu.com/{href}"
        chapter_content = fetch_chapter_content(chapter_url, proxy)

        # 保存章节内容到txt文件
        if chapter_content:
            with open(chapter_file, "w", encoding="utf-8") as f:
                f.write(chapter_content)


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="下载小说的章节内容")
    parser.add_argument("novelid", help="小说的ID, 例如: n2267be")
    parser.add_argument("-p", "--proxy", help="设置代理, 例如: socks5h://127.0.0.1:1080")
    args = parser.parse_args()

    page = 1
    all_chapters = []
    novel_title = ""

    # 获取小说所有章节的列表
    while True:
        print(f"正在获取第 {page} 页 ...")
        chapters, title, next_page_url = fetch_chapters(args.novelid, page, args.proxy)

        if not chapters:
            print("没有获取到章节信息，停止抓取。")
            break

        # 存储章节信息和小说标题
        if not novel_title:
            novel_title = title  # 只记录第一次获取到的小说标题

        all_chapters.extend(chapters)

        # 如果没有下一页，停止
        if not next_page_url:
            print("抓取完毕，停止获取更多页面。")
            break

        page += 1

    # 将所有章节保存到文件中
    if all_chapters:
        save_chapters_to_file(novel_title, all_chapters, args.proxy)


if __name__ == '__main__':
    main()
