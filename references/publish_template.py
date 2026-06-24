#!/usr/bin/env python3
"""
微信公众号读书拆解发布脚本模板
使用 scripts/ 目录下的模块

用法：
  1. 填写下方的变量（标题、摘要、HTML内容等）
  2. 确保封面图已准备好（使用 scripts/book_cover.py 获取）
  3. 运行: python3 references/publish_template.py
"""

import os
import sys

# 添加 scripts 目录到模块搜索路径
scripts_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"
)
sys.path.insert(0, scripts_dir)

from wechat_api import load_config, get_access_token, upload_cover, create_draft


# ========== 替换以下内容 ==========

# 标题和摘要
TITLE = "《书名》全书深度拆解：犀利洞察"
AUTHOR = "读书笔记"
DIGEST = "摘要文本，不超过120字。"

# 封面图目录（包含 cover_900x500.jpg）
COVER_DIR = "/tmp/book_output"

# 主题色：主色（深色）+ 强调色（暖/亮色）
T = "#2E5266"  # 主色
T2 = "#D4A24C"  # 强调色
BODY = "#555"  # 正文色
CBG = "#F0EDE5"  # 引用块背景

# 文章 HTML 内容（7段式，无数字编号）
HTML = f"""<section style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#333;background:#FBF8FC;">

  <p style="font-size:12px;color:{T2};text-align:center;letter-spacing:4px;margin:24px 0 8px;line-height:3em;">
    <span>📖 读书拆解</span>
  </p>

  <p style="font-size:22px;font-weight:bold;color:{T};text-align:center;margin:0 0 6px;line-height:1.5;">
    <span>《书名》全书深度拆解</span>
  </p>

  <p style="font-size:14px;color:#999;text-align:center;margin:0 0 20px;line-height:3em;">
    <span>副标题（一句话点睛）</span>
  </p>

  <!-- 书籍封面图（第一张图） -->
  <p style="margin:0 0 20px;text-align:center;">
    <img src="http://mmbiz.qpic.cn/REPLACE_WITH_BOOK_COVER_URL" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="《书名》封面"/>
  </p>

  <!-- 作者背景与创作时代（无数字编号） -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>作者背景与创作时代</span>
  </p>

  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>正文段落。注意：所有段落必须有 text-indent:2em。</span>
  </p>

  <p style="font-size:17px;line-height:1.9;color:{T};font-weight:bold;text-indent:2em;margin:0 0 20px;padding:14px 18px;background:{CBG};border-radius:8px;">
    <span>引用块：金句或核心观点。</span>
  </p>

  <!-- 其他章节 -->

  <p style="font-size:14px;color:#ccc;text-align:center;letter-spacing:8px;margin:20px 0;">· · · · · ·</p>

  <!-- 星级评分与适配人群 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>星级评分与适配人群</span>
  </p>

  <p style="font-size:28px;text-align:center;margin:0 0 8px;">
    <span style="color:{T2};">★★★★☆</span>
  </p>

  <p style="font-size:16px;color:{BODY};text-align:center;margin:0 0 16px;">
    <span>4 / 5 星</span>
  </p>

  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>为什么给X星？简要说明评分理由。</span>
  </p>

  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 8px;text-indent:2em;">
    <strong style="color:{T};">适合人群：</strong>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>✓ 人群1——具体理由<br/>✓ 人群2——具体理由<br/>✓ 人群3——具体理由</span>
  </p>

  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 8px;text-indent:2em;">
    <strong style="color:{T};">不适合人群：</strong>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>✗ 人群1——具体理由<br/>✗ 人群2——具体理由<br/>✗ 人群3——具体理由</span>
  </p>

  <p style="font-size:14px;color:#ccc;text-align:center;letter-spacing:8px;margin:20px 0;">· · · · · ·</p>

  <p style="font-size:16px;line-height:2;color:{T};text-align:center;margin:0 0 4px;font-weight:bold;text-indent:2em;">
    <span>📖 《书名》作者 · 读书笔记</span>
  </p>
  <p style="font-size:14px;color:#999;text-align:center;margin:0 0 4px;text-indent:2em;">
    <span>一句话总结</span>
  </p>

</section>"""


def main():
    print("=" * 50)
    print("微信公众号 - 书名 发布")
    print("=" * 50)

    # 1. 加载配置和获取token
    config = load_config()
    token = get_access_token(config)
    print("\n✓ Token 已获取\n")

    # 2. 上传封面图
    cover_900_path = os.path.join(COVER_DIR, "cover_900x500.jpg")
    if not os.path.exists(cover_900_path):
        print(f"错误: 封面图不存在 {cover_900_path}", file=sys.stderr)
        print("请先运行: python3 scripts/book_cover.py '书名' '作者'", file=sys.stderr)
        sys.exit(1)

    print("上传封面图...")
    cover_mid = upload_cover(token, cover_900_path)

    # 3. 创建草稿
    print("\n创建草稿...")
    draft_id = create_draft(token, TITLE, AUTHOR, DIGEST, HTML, cover_mid)

    print("\n" + "=" * 50)
    print("发布成功!")
    print("=" * 50)
    print(f"标题:   {TITLE}")
    print(f"作者:   {AUTHOR}")
    print(f"草稿ID: {draft_id}")
    print(f"\n请前往微信公众平台查看草稿:")
    print(f"https://mp.weixin.qq.com")


if __name__ == "__main__":
    main()
