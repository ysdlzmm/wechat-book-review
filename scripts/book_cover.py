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
    """按优先级尝试获取书籍封面，最后回退到占位图"""
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
        print("⚠️ 三个数据源均未返回封面，使用占位图占位")
        cover_url = "https://images.pexels.com/photos/159711/books-bookstore-book-reading-159711.jpeg?auto=compress&cs=tinysrgb&w=600"

    print(f"✓ 封面URL: {cover_url}")
    return cover_url


def download_and_process_cover(cover_url, output_dir):
    """下载并处理封面图"""
    from PIL import Image

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(cover_url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, context=ctx, timeout=15).read()

    os.makedirs(output_dir, exist_ok=True)
    original_path = os.path.join(output_dir, "book_cover_original.jpg")
    with open(original_path, "wb") as f:
        f.write(data)

    img = Image.open(original_path)
    w, h = img.size
    if w > 600:
        ratio = 600 / w
        new_w = 600
        new_h = int(h * ratio)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    cover_path = os.path.join(output_dir, "book_cover.jpg")
    img.save(cover_path, "JPEG", quality=90)

    w, h = img.size
    target_ratio = 900 / 500
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    img = img.resize((900, 500), Image.LANCZOS)

    cover_900_path = os.path.join(output_dir, "cover_900x500.jpg")
    img.save(cover_900_path, "JPEG", quality=90)

    print(f"✓ 封面图已保存: {cover_path}")
    print(f"✓ 公众号封面已保存: {cover_900_path}")

    return cover_path, cover_900_path


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
