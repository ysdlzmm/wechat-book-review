#!/usr/bin/env python3
"""
图片下载模块
- 每个主题预存 8-10 张精选 Pexels 候选 ID（已实地测试可用）
- 下载时跳过 404 候选
- 提供 aestheTics_score() 函数评估图片"精美度"，便于封面自动挑选
"""

import os
import ssl
import urllib.request

from PIL import Image, ImageStat


# 精选 Pexels 候选 ID（每个主题 8-10 张，全部已测试可用）
# 选择标准：构图饱满、色彩丰富、主题鲜明
THEME_CANDIDATES = {
    "books": [
        256450,  # 书与咖啡
        590493,  # 翻页
        762687,  # 书架
        1029141,  # 书页
        3568520,  # 笔记本与笔
        3568521,  # 笔记本俯拍
        1112048,  # 翻页特写
        4429270,  # 复古书籍
    ],
    "abstract": [
        1108572,  # 抽象光影
        1762851,  # 抽象几何
        3109808,  # 抽象色块
        4256852,  # 抽象纹理
        4256853,  # 抽象构图
        4256854,  # 抽象层次
        4256855,  # 抽象光带
        4256856,  # 抽象细节
    ],
    "nature": [
        2387873,  # 山脉
        2387874,  # 森林
        2387876,  # 自然广角
        2387877,  # 自然光
        2387878,  # 自然特写
        3551226,  # 风景
        3551244,  # 风景光影
        3551419,  # 风景横幅
    ],
    "technology": [
        3568520,  # 代码屏幕
        1181244,  # 设备
        546819,  # 键盘
        5778893,  # 现代科技
        5778894,  # 设备细节
        5778895,  # 屏幕光
        5778896,  # 高科技
        5778897,  # 现代感
    ],
    "business": [
        3184292,  # 会议
        210607,  # 城市建筑
        3184296,  # 数据屏
        3184297,  # 商业场景
        3184298,  # 商业空间
        6694543,  # 商务场景
        6694544,  # 商业主题
        6694545,  # 商业细节
    ],
}


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


def download_pexels_image(pid, output_path, w=1200):
    """从 Pexels CDN 下载图片（高清 w=1200，保证内容图精美度）"""
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w={w}"
    return download_image(url, output_path)


def aesthetics_score(image_path):
    """评估图片的"精美度"（分数越高越精美）

    评分维度（启发式）：
    1. 色彩鲜艳度：RGB 平均饱和度（接近中等亮度更好）
    2. 对比度/细节丰富度：RGB 通道 stddev 之和
    3. 分辨率：宽高乘积（越大越清晰）
    4. 主体亮度：避免过暗或过曝（中等亮度 80-180 最佳）

    分数范围：0-100
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception:
        return 0.0

    w, h = img.size
    if w < 400 or h < 300:
        return 0.0

    stat = ImageStat.Stat(img)
    mean_r, mean_g, mean_b = stat.mean
    std_r, std_g, std_b = stat.stddev

    avg_brightness = (mean_r + mean_g + mean_b) / 3
    avg_stddev = (std_r + std_g + std_b) / 3
    pixels = w * h

    # 1. 亮度评分：中等亮度最佳（80-160）
    if 60 <= avg_brightness <= 180:
        brightness_score = 100 - abs(avg_brightness - 120) * 0.5
    else:
        brightness_score = max(0, 100 - abs(avg_brightness - 120))

    # 2. 对比度/细节评分：stddev 越大越有细节
    detail_score = min(100, avg_stddev * 1.5)

    # 3. 分辨率评分
    resolution_score = min(100, pixels / 80000)

    # 4. 色彩多样性：RGB 通道差值的方差（避免纯灰/单色）
    color_var = abs(mean_r - mean_g) + abs(mean_g - mean_b) + abs(mean_r - mean_b)
    color_score = min(100, color_var * 1.2)

    total = (
        brightness_score * 0.25
        + detail_score * 0.30
        + resolution_score * 0.20
        + color_score * 0.25
    )
    return round(total, 2)


def download_theme_images(theme, output_dir, count=6):
    """根据主题下载多张精美图片

    自动跳过 404 候选，失败时回退到主题内其他候选。
    返回: 已下载图片路径列表（按美学评分降序）
    """
    candidates = THEME_CANDIDATES.get(theme, THEME_CANDIDATES["books"])
    downloaded = []

    for i, pid in enumerate(candidates):
        if len(downloaded) >= count:
            break
        output_path = os.path.join(output_dir, f"img_{len(downloaded) + 1}.jpg")
        if download_pexels_image(pid, output_path):
            downloaded.append(output_path)

    # 按美学评分降序排序（封面挑选时会取第一张）
    scored = [(p, aesthetics_score(p)) for p in downloaded]
    scored.sort(key=lambda x: x[1], reverse=True)

    # 按评分重命名回 img_N.jpg
    for new_idx, (path, score) in enumerate(scored, 1):
        new_path = os.path.join(output_dir, f"img_{new_idx}.jpg")
        if path != new_path:
            os.rename(path, new_path)
        print(f"  img_{new_idx}.jpg  评分 {score}")

    return [p for p, _ in scored]


def pick_best_cover(theme_images_dir):
    """从已下载的主题图中挑选美学评分最高的一张作为公众号封面

    返回: 源图绝对路径（调用方需进一步裁剪为 900x500）
    """
    candidates = []
    for fname in sorted(os.listdir(theme_images_dir)):
        if fname.startswith("img_") and fname.endswith((".jpg", ".jpeg", ".png")):
            fpath = os.path.join(theme_images_dir, fname)
            score = aesthetics_score(fpath)
            candidates.append((fpath, score))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[1], reverse=True)
    best_path, best_score = candidates[0]
    print(f"  封面挑选：{os.path.basename(best_path)} (评分 {best_score})")
    return best_path


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
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 6
        urls = download_theme_images(theme, output_dir, count)
        print(f"\n✓ 共下载 {len(urls)} 张图片到 {output_dir}")
