#!/usr/bin/env python3
"""
书籍封面图获取模块
支持：Google Books API、Open Library API、豆瓣搜索
"""

import json
import os
import re
import ssl
import urllib.request
import urllib.parse


def fetch_book_cover_google(book_title, author=""):
    """通过 Google Books API 获取书籍封面"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    query = f"intitle:{book_title}"
    if author:
        query += f"+inauthor:{author}"

    url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(query)}&maxResults=1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        data = urllib.request.urlopen(req, context=ctx, timeout=15).read()
        result = json.loads(data)

        if "items" in result and len(result["items"]) > 0:
            volume = result["items"][0]["volumeInfo"]
            if "imageLinks" in volume:
                cover_url = volume["imageLinks"].get("large") or volume[
                    "imageLinks"
                ].get("thumbnail")
                if cover_url:
                    cover_url = cover_url.replace("http://", "https://").replace(
                        "&edge=curl", ""
                    )
                    return cover_url
    except Exception as e:
        print(f"Google Books API 获取失败: {e}")

    return None


def fetch_book_cover_openlibrary(isbn):
    """通过 Open Library 获取书籍封面（需要 ISBN）"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        response = urllib.request.urlopen(req, context=ctx, timeout=15)
        if response.status == 200:
            return url
    except Exception as e:
        print(f"Open Library 获取失败: {e}")

    return None


def fetch_book_cover_douban(book_title, author=""):
    """通过豆瓣搜索获取书籍封面（需解析 HTML）"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    query = f"{book_title} {author}".strip()
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.douban.com/book/subject_search?search_text={encoded_query}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )

    try:
        raw = urllib.request.urlopen(req, context=ctx, timeout=15).read()
        html = raw.decode("utf-8", errors="replace")
        match = re.search(
            r'<img[^>]+src="(https://img[0-9]+\.doubanio\.com/view/subject/[^"]+)"',
            html,
        )
        if match:
            return match.group(1)
    except Exception as e:
        print(f"豆瓣搜索获取失败: {e}")

    return None


def fetch_book_cover(book_title, author="", isbn=""):
    """按优先级尝试获取书籍封面（书籍原图），最后回退到占位图

    注意：此函数返回的是书籍原图，仅用于 article 内首图占位。
    公众号封面（cover_900x500.jpg）现在改用主题贴图，与正文风格统一。
    如需主题封面，请调用 fetch_theme_cover()。
    """
    cover_url = None

    print(f"尝试从 Google Books 获取《{book_title}》封面...")
    cover_url = fetch_book_cover_google(book_title, author)

    if not cover_url and isbn:
        print(f"尝试从 Open Library 获取封面...")
        cover_url = fetch_book_cover_openlibrary(isbn)

    if not cover_url:
        print(f"尝试从豆瓣获取封面...")
        cover_url = fetch_book_cover_douban(book_title, author)

    if not cover_url:
        print("⚠️ 三个数据源均未返回书籍封面，回退到占位图")
        cover_url = "https://images.pexels.com/photos/159711/books-bookstore-book-reading-159711.jpeg?auto=compress&cs=tinysrgb&w=600"

    print(f"✓ 书籍封面URL: {cover_url}")
    return cover_url


# 每个主题对应 3 张精选的 900x500 Pexels 封面图（fit=crop 自动精确裁切）
# 选用宽高比接近 1.8 的高质量原图，避免裁切损失重要内容
THEME_COVER_CANDIDATES = {
    "abstract": [1108572, 1762851, 3109808],
    "books": [256450, 590493, 762687],
    "nature": [2387873, 2387874, 2387876],
    "technology": [3568520, 1181244, 546819],
    "business": [3184292, 210607, 3184296],
}


def _build_cover_url(pid, w=900, h=500):
    """构造 Pexels CDN URL，含精确 900x500 fit=crop 裁切参数"""
    return f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}&h={h}&fit=crop"


def fetch_theme_cover(theme="abstract", seed=0):
    """从 Pexels CDN 获取一张与主题对应的 900x500 精确封面 URL（不裁剪原图）"""
    candidates = THEME_COVER_CANDIDATES.get(theme, THEME_COVER_CANDIDATES["abstract"])
    pid = candidates[seed % len(candidates)]
    url = _build_cover_url(pid)
    print(f"✓ 主题封面URL ({theme}, pid={pid}): {url}")
    return url


def download_cover_900x500(theme="abstract", output_dir="/tmp", seed=0):
    """下载一张 900x500 的主题封面图（Pexels 服务端精确裁剪，无需本地处理）

    返回: cover_900x500.jpg 绝对路径
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    os.makedirs(output_dir, exist_ok=True)
    cover_900_path = os.path.join(output_dir, "cover_900x500.jpg")

    candidates = THEME_COVER_CANDIDATES.get(theme, THEME_COVER_CANDIDATES["abstract"])
    # 顺序尝试每个候选 PID，跳过 404
    for i, pid in enumerate(candidates):
        idx = (seed + i) % len(candidates)
        pid_try = candidates[idx]
        url = _build_cover_url(pid_try)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, context=ctx, timeout=15).read()
            with open(cover_900_path, "wb") as f:
                f.write(data)
            print(f"✓ 公众号封面已下载 ({theme}, pid={pid_try}): {cover_900_path}")
            return cover_900_path
        except Exception as e:
            print(f"  候选 pid={pid_try} 失败: {e}")
            continue

    raise RuntimeError(f"主题 {theme} 的所有候选封面均下载失败")


def download_and_process_cover(cover_url, output_dir):
    """从主题贴图URL下载并处理为 600px 文章封面（兼容旧调用）"""
    from PIL import Image

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(cover_url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, context=ctx, timeout=15).read()

    os.makedirs(output_dir, exist_ok=True)
    original_path = os.path.join(output_dir, "theme_cover_original.jpg")
    with open(original_path, "wb") as f:
        f.write(data)

    img = Image.open(original_path)
    w, h = img.size
    if w > 600:
        ratio = 600 / w
        img = img.resize((600, int(h * ratio)), Image.LANCZOS)
    img.save(os.path.join(output_dir, "theme_cover_600.jpg"), "JPEG", quality=90)

    print(f"✓ 主题封面(600px)已保存: theme_cover_600.jpg")
    return os.path.join(output_dir, "theme_cover_600.jpg"), None


def crop_cover_from_local(source_path, output_dir):
    """兼容旧 API：建议改用 download_cover_900x500()"""
    print("⚠️ crop_cover_from_local 已弃用，请改用 download_cover_900x500(theme=...)")
    return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python book_cover.py <书名> [作者] [ISBN]")
        sys.exit(1)

    title = sys.argv[1]
    author = sys.argv[2] if len(sys.argv) > 2 else ""
    isbn = sys.argv[3] if len(sys.argv) > 3 else ""

    url = fetch_book_cover(title, author, isbn)
    if url:
        download_and_process_cover(url, "/tmp/book_cover")
