#!/usr/bin/env python3
"""
微信公众号读书拆解发布脚本
完整流程：获取封面 -> 下载插图 -> 上传图片 -> 创建草稿
"""

import argparse
import json
import os
import sys

# 添加当前目录到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from book_cover import fetch_book_cover, download_and_process_cover
from image_downloader import download_theme_images
from wechat_api import (
    load_config,
    get_access_token,
    upload_cover,
    upload_content_image,
    create_draft,
)


def ensure_book_cover(cover_dir, book_title="", book_author="", book_isbn=""):
    """确保封面图存在，缺失则自动获取"""
    cover_900_path = os.path.join(cover_dir, "cover_900x500.jpg")
    book_cover_path = os.path.join(cover_dir, "book_cover.jpg")

    if os.path.exists(cover_900_path) and os.path.exists(book_cover_path):
        print("✓ 封面图已存在，跳过获取")
        return

    if not book_title:
        print(
            f"⚠️ 缺少封面图且未提供 --book-title，无法自动获取。\n"
            f"  期望路径: {cover_900_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"封面图缺失，自动获取《{book_title}》封面...")
    os.makedirs(cover_dir, exist_ok=True)
    cover_url = fetch_book_cover(book_title, book_author, book_isbn)
    if not cover_url:
        print("错误: 无法获取书籍封面URL", file=sys.stderr)
        sys.exit(1)
    download_and_process_cover(cover_url, cover_dir)


def ensure_theme_images(cover_dir, theme="abstract", count=5):
    """确保主题插图存在，缺失则自动下载"""
    existing = [
        f
        for f in os.listdir(cover_dir)
        if f.startswith("img_") and f.endswith((".jpg", ".jpeg", ".png"))
    ]
    if len(existing) >= count:
        print(f"✓ 主题插图已存在 {len(existing)} 张，跳过下载")
        return

    print(f"主题插图不足，自动下载 {count} 张（主题: {theme}）...")
    download_theme_images(theme, cover_dir, count)


def publish_article(
    title,
    author,
    digest,
    content_html,
    cover_dir,
    theme="abstract",
    image_count=5,
    book_title="",
    book_author="",
    book_isbn="",
):
    """完整发布流程：获取封面 -> 下载插图 -> 上传图片 -> 创建草稿"""
    print("=" * 50)
    print("微信公众号 - 书评发布")
    print("=" * 50)

    os.makedirs(cover_dir, exist_ok=True)

    # 1. 确保封面图存在
    print("\n[1/4] 准备封面图...")
    ensure_book_cover(cover_dir, book_title, book_author, book_isbn)

    # 2. 确保主题插图存在
    print("\n[2/4] 准备主题插图...")
    ensure_theme_images(cover_dir, theme, image_count)

    # 3. 加载配置和获取token
    config = load_config()
    token = get_access_token(config)
    print("\n✓ Token 已获取\n")

    # 4. 上传封面图
    cover_900_path = os.path.join(cover_dir, "cover_900x500.jpg")
    if not os.path.exists(cover_900_path):
        print(f"错误: 封面图不存在 {cover_900_path}", file=sys.stderr)
        sys.exit(1)

    print("上传封面图...")
    cover_mid = upload_cover(token, cover_900_path)

    # 5. 上传内容图片
    print("\n上传内容图片...")
    image_urls = {}
    for fname in sorted(os.listdir(cover_dir)):
        if fname.startswith("img_") and fname.endswith((".jpg", ".jpeg", ".png")):
            fpath = os.path.join(cover_dir, fname)
            url = upload_content_image(token, fpath)
            if url:
                name = os.path.splitext(fname)[0]
                image_urls[name] = url

    # 6. 上传书籍封面图（用于文章内显示）
    book_cover_path = os.path.join(cover_dir, "book_cover.jpg")
    if os.path.exists(book_cover_path):
        book_cover_url = upload_content_image(token, book_cover_path)
        if book_cover_url:
            image_urls["book_cover"] = book_cover_url

    # 7. 保存上传结果
    result_path = os.path.join(cover_dir, "upload_result.json")
    with open(result_path, "w") as f:
        json.dump(
            {
                "cover_mid": cover_mid,
                "image_urls": image_urls,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\n✓ 上传结果已保存: {result_path}")

    # 8. 创建草稿
    print("\n创建草稿...")
    draft_id = create_draft(token, title, author, digest, content_html, cover_mid)

    print("\n" + "=" * 50)
    print("发布成功!")
    print("=" * 50)
    print(f"标题:   {title}")
    print(f"作者:   {author}")
    print(f"草稿ID: {draft_id}")
    print(f"\n请前往微信公众平台查看草稿:")
    print(f"https://mp.weixin.qq.com")

    return draft_id


def main():
    parser = argparse.ArgumentParser(description="微信公众号书评发布工具")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--author", default="读书笔记", help="作者名称")
    parser.add_argument("--digest", default="", help="文章摘要")
    parser.add_argument("--content-file", required=True, help="HTML内容文件路径")
    parser.add_argument("--cover-dir", required=True, help="封面和图片目录")
    parser.add_argument("--theme", default="abstract", help="图片主题")
    parser.add_argument("--image-count", type=int, default=5, help="主题插图数量")
    parser.add_argument("--book-title", default="", help="书籍标题（缺封面时自动获取）")
    parser.add_argument("--book-author", default="", help="书籍作者")
    parser.add_argument("--book-isbn", default="", help="书籍ISBN")
    args = parser.parse_args()

    with open(args.content_file, "r", encoding="utf-8") as f:
        content_html = f.read()

    publish_article(
        args.title,
        args.author,
        args.digest,
        content_html,
        args.cover_dir,
        args.theme,
        args.image_count,
        args.book_title,
        args.book_author,
        args.book_isbn,
    )


if __name__ == "__main__":
    main()
