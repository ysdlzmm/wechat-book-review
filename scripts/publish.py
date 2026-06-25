#!/usr/bin/env python3
"""
微信公众号读书拆解发布脚本
完整流程：准备主题贴图 -> 裁剪公众号封面 -> 上传图片 -> 创建草稿
"""

import argparse
import json
import os
import sys

# 添加当前目录到模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from book_cover import crop_cover_from_local, fetch_theme_cover
from image_downloader import download_theme_images
from wechat_api import (
    load_config,
    get_access_token,
    upload_cover,
    upload_content_image,
    create_draft,
)


def ensure_theme_images(cover_dir, theme="abstract", count=6):
    """确保主题插图存在，缺失则自动下载

    默认 6 张：用于正文穿插（5 张）+ 结尾页（1 张）= 6 张
    """
    os.makedirs(cover_dir, exist_ok=True)
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


def ensure_cover_image(cover_dir, theme="abstract"):
    """确保公众号封面（900x500）存在，缺失则从主题图裁剪"""
    cover_900_path = os.path.join(cover_dir, "cover_900x500.jpg")
    if os.path.exists(cover_900_path):
        print("✓ 公众号封面已存在，跳过裁剪")
        return

    # 优先用本地第一张主题图裁剪；否则从主题URL下载
    candidates = sorted(
        [
            f
            for f in os.listdir(cover_dir)
            if f.startswith("img_") and f.endswith((".jpg", ".jpeg", ".png"))
        ]
    )
    if candidates:
        crop_cover_from_local(os.path.join(cover_dir, candidates[0]), cover_dir)
    else:
        # 极少见：连主题图都没有的情况
        print("主题图与封面均缺失，从网络拉取主题封面...")
        from book_cover import download_and_process_cover

        url = fetch_theme_cover(theme)
        download_and_process_cover(url, cover_dir)


def publish_article(
    title,
    author,
    digest,
    content_html,
    cover_dir,
    theme="abstract",
    image_count=6,
):
    """完整发布流程：准备主题贴图 -> 裁剪公众号封面 -> 上传图片 -> 创建草稿"""
    print("=" * 50)
    print("微信公众号 - 书评发布")
    print("=" * 50)

    os.makedirs(cover_dir, exist_ok=True)

    # 1. 准备主题贴图
    print("\n[1/4] 准备主题贴图...")
    ensure_theme_images(cover_dir, theme, image_count)

    # 2. 准备公众号封面（900x500）
    print("\n[2/4] 准备公众号封面...")
    ensure_cover_image(cover_dir, theme)

    # 3. 加载配置和获取 token
    config = load_config()
    token = get_access_token(config)
    print("\n✓ Token 已获取\n")

    # 4. 上传公众号封面
    cover_900_path = os.path.join(cover_dir, "cover_900x500.jpg")
    if not os.path.exists(cover_900_path):
        print(f"错误: 封面图不存在 {cover_900_path}", file=sys.stderr)
        sys.exit(1)

    print("上传公众号封面...")
    cover_mid = upload_cover(token, cover_900_path)

    # 5. 上传内容图片（img_*.jpg）
    print("\n上传内容图片...")
    image_urls = {}
    for fname in sorted(os.listdir(cover_dir)):
        if fname.startswith("img_") and fname.endswith((".jpg", ".jpeg", ".png")):
            fpath = os.path.join(cover_dir, fname)
            url = upload_content_image(token, fpath)
            if url:
                name = os.path.splitext(fname)[0]
                image_urls[name] = url

    # 6. 保存上传结果
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

    # 7. 创建草稿
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
    parser.add_argument(
        "--image-count", type=int, default=6, help="主题插图数量（默认6：5正文+1结尾）"
    )
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
    )


if __name__ == "__main__":
    main()
