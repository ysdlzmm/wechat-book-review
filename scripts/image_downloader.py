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
        "nature": [15286, 15287, 15288, 15289, 15290],
        "technology": [1181244, 1181245, 1181246, 1181247, 1181248],
        "abstract": [2693208, 2693209, 2693210, 2693211, 2693212],
        "books": [159711, 159712, 159713, 159714, 159715],
        "business": [3184292, 3184293, 3184294, 3184295, 3184296],
    }

    pids = themes.get(theme, themes["abstract"])[:count]
    urls = []

    for i, pid in enumerate(pids):
        output_path = os.path.join(output_dir, f"img_{i + 1}.jpg")
        if download_pexels_image(pid, output_path):
            urls.append(output_path)

    return urls


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python image_downloader.py <图片URL> [输出路径]")
        sys.exit(1)

    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "/tmp/downloaded_image.jpg"
    download_image(url, output)
