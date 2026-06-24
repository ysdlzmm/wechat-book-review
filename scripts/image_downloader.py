#!/usr/bin/env python3
"""
图片下载模块
支持：Pexels CDN、通用URL下载
"""

import os
import ssl
import urllib.request


def download_image(url, output_path):
    """下载图片到指定路径"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        data = urllib.request.urlopen(req, context=ctx, timeout=15).read()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False


def download_pexels_image(pid, output_path):
    """从 Pexels CDN 下载图片"""
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1080"
    return download_image(url, output_path)


def download_theme_images(theme, output_dir, count=5):
    """根据主题下载多张图片"""
    themes = {
        "nature": [2387873, 2387874, 2387875, 2387876, 2387877, 2387878, 2387879],
        "technology": [3568520, 3568521, 3568522, 3568523, 3568524, 3568525],
        "abstract": [2693208, 2693209, 2693210, 2693211, 2693212, 2693213],
        "books": [159711, 1029141, 256450, 590493, 762687, 3568520],
        "business": [3184292, 3184293, 3184294, 3184295, 3184296, 3184297],
    }

    pids = themes.get(theme, themes["abstract"])[:count]
    urls = []
    fallback_pid = 159711
    fallback_used = False

    for i, pid in enumerate(pids):
        output_path = os.path.join(output_dir, f"img_{i + 1}.jpg")
        if download_pexels_image(pid, output_path):
            urls.append(output_path)
        elif not fallback_used:
            if download_pexels_image(fallback_pid, output_path):
                urls.append(output_path)
                fallback_used = True

    return urls


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python image_downloader.py <图片URL> [输出路径]")
        print("  python image_downloader.py <主题> <输出目录> [数量]")
        sys.exit(1)

    arg1 = sys.argv[1]
    if arg1.startswith("http://") or arg1.startswith("https://"):
        url = arg1
        output = sys.argv[2] if len(sys.argv) > 2 else "/tmp/downloaded_image.jpg"
        download_image(url, output)
    else:
        theme = arg1
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "/tmp/images"
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        urls = download_theme_images(theme, output_dir, count)
        print(f"\n✓ 共下载 {len(urls)} 张图片到 {output_dir}")
