#!/usr/bin/env python3
"""
微信公众号读书拆解发布脚本模板
使用 scripts/ 目录下的模块

用法：
  1. 填写下方的变量（标题、摘要、HTML内容等）
  2. 确保封面图已准备好（使用 scripts/image_downloader.py 下载主题贴图）
  3. 运行: python3 references/publish_template.py
"""

import os
import sys

scripts_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"
)
sys.path.insert(0, scripts_dir)

from wechat_api import load_config, get_access_token, upload_cover, create_draft


# ========== 替换以下内容 ==========

TITLE = "《书名》全书深度拆解：犀利洞察"
AUTHOR = "读书笔记"
DIGEST = "摘要文本，不超过120字。"

# 封面图目录（包含 cover_900x500.jpg + img_*.jpg 主题贴图）
COVER_DIR = "/tmp/book_output"

# 主题色：主色（深色）+ 强调色（暖/亮色）
T = "#2E5266"  # 主色
T2 = "#D4A24C"  # 强调色
BODY = "#555"  # 正文色
CBG = "#F0EDE5"  # 引用块背景

# 图片 URL（替换为上传微信后返回的 mmbiz.qpic.cn URL）
# 通过 publish.py 自动上传后，从 upload_result.json 中获取
THEME_IMG_1 = "http://mmbiz.qpic.cn/REPLACE_WITH_THEME_IMG_1"
THEME_IMG_2 = "http://mmbiz.qpic.cn/REPLACE_WITH_THEME_IMG_2"
THEME_IMG_3 = "http://mmbiz.qpic.cn/REPLACE_WITH_THEME_IMG_3"
THEME_IMG_4 = "http://mmbiz.qpic.cn/REPLACE_WITH_THEME_IMG_4"
THEME_IMG_5 = "http://mmbiz.qpic.cn/REPLACE_WITH_THEME_IMG_5"
THEME_IMG_END = "http://mmbiz.qpic.cn/REPLACE_WITH_THEME_IMG_END"

# 文章 HTML 内容（7段式，无数字编号，全文主题贴图穿插）
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

  <!-- 主题配图1（头部） -->
  <p style="margin:0 0 20px;text-align:center;">
    <img src="{THEME_IMG_1}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="主题配图"/>
  </p>

  <!-- 先搞懂写书的这个人 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>先搞懂写书的这个人</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>正文段落。所有段落必须有 text-indent:2em。重点句用 <strong style="color:{T};background:{CBG};padding:1px 6px;border-radius:3px;">主题主色高亮</strong>，核心概念用 <span style="color:{T2};font-weight:bold;">强调色加粗</span>。</span>
  </p>

  <!-- 主题配图2（先搞懂写书的这个人后） -->
  <p style="margin:0 0 20px;text-align:center;">
    <img src="{THEME_IMG_2}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="主题配图"/>
  </p>

  <!-- 金句引用块（左侧色条 + 主题色加粗） -->
  <p style="font-size:17px;line-height:1.9;color:{T};font-weight:bold;text-indent:2em;margin:0 0 20px;padding:14px 18px;background:{CBG};border-left:4px solid {T2};border-radius:6px;">
    <span style="color:{T2};">▍</span> 金句或核心观点。整段用主题主色加粗，加左侧强调色条与正文形成视觉对比。
  </p>

  <!-- 全书脉络 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>全书脉络</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>本章按章节脉络梳理<strong style="color:{T};background:{CBG};padding:1px 6px;border-radius:3px;">全书核心逻辑</strong>，用文字框图提炼主线。</span>
  </p>

  <!-- 主题配图3（逻辑导图后） -->
  <p style="margin:0 0 20px;text-align:center;">
    <img src="{THEME_IMG_3}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="主题配图"/>
  </p>

  <!-- 三个颠覆认知的真相 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>三个颠覆认知的真相</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span><span style="color:{T2};font-weight:bold;">论点一：</span><strong style="color:{T};background:{CBG};padding:1px 6px;border-radius:3px;">核心颠覆性观点</strong>，附书中具体案例支撑。</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span><span style="color:{T2};font-weight:bold;">论点二：</span><strong style="color:{T};background:{CBG};padding:1px 6px;border-radius:3px;">核心颠覆性观点</strong>，附书中具体案例支撑。</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span><span style="color:{T2};font-weight:bold;">论点三：</span><strong style="color:{T};background:{CBG};padding:1px 6px;border-radius:3px;">核心颠覆性观点</strong>，附书中具体案例支撑。</span>
  </p>

  <!-- 主题配图4（论点后） -->
  <p style="margin:0 0 20px;text-align:center;">
    <img src="{THEME_IMG_4}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="主题配图"/>
  </p>

  <!-- 这本书的短板，不吐不快 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>这本书的短板，不吐不快</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>短板一：客观指出书中局限。<br/>短板二：逻辑漏洞分析。<br/>短板三：适用边界。<br/>短板四：时代局限。</span>
  </p>

  <!-- 金句二 -->
  <p style="font-size:17px;line-height:1.9;color:{T};font-weight:bold;text-indent:2em;margin:0 0 20px;padding:14px 18px;background:{CBG};border-left:4px solid {T2};border-radius:6px;">
    <span style="color:{T2};">▍</span> 第二个金句或关键启发。
  </p>

  <!-- 读完真正留下的东西 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>读完真正留下的东西</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>读完能带走的<strong style="color:{T};background:{CBG};padding:1px 6px;border-radius:3px;">三样东西</strong>，从个人成长视角展开。</span>
  </p>

  <!-- 主题配图5（读完真正留下的东西后） -->
  <p style="margin:0 0 20px;text-align:center;">
    <img src="{THEME_IMG_5}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="主题配图"/>
  </p>

  <!-- 四条拿来就用的行动项 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>四条拿来就用的行动项</span>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>方案一：具体执行步骤。<br/>方案二：可操作建议。<br/>方案三：拿来就用的行动项。</span>
  </p>

  <p style="font-size:14px;color:#ccc;text-align:center;letter-spacing:8px;margin:20px 0;">· · · · · ·</p>

  <!-- 值不值得花时间读 -->
  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
    <span>值不值得花时间读</span>
  </p>

  <p style="font-size:28px;text-align:center;margin:0 0 8px;">
    <span style="color:{T2};">★★★★☆</span>
  </p>

  <p style="font-size:16px;color:{BODY};text-align:center;margin:0 0 16px;">
    <span>4 / 5 星</span>
  </p>

  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>为什么给X星？简要说明评分理由，诚实评价，3-4星是常态，5星极少。</span>
  </p>

  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 8px;text-indent:2em;">
    <strong style="color:{T};">适合人群：</strong>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>✅&nbsp;&nbsp;创业者/管理者——理解系统脆弱性和反脆弱设计<br />✅&nbsp;&nbsp;对个人成长感兴趣的读者——掌握从压力中受益的方法<br />✅&nbsp;&nbsp;对决策科学感兴趣的读者——理解非线性风险的本质</span>
  </p>

  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 8px;text-indent:2em;">
    <strong style="color:{T};">不适合人群：</strong>
  </p>
  <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>🚫&nbsp;&nbsp;已读过类似书籍的人——内容高度重复<br />🚫&nbsp;&nbsp;讨厌抽象论证的人——本书充满概念性思维<br />🚫&nbsp;&nbsp;寻找具体操作手册的人——本书偏哲学思辨</span>
  </p>

  <!-- 结尾页：主题配图 + 书名 + 作者 + 核心总结 -->
  <p style="margin:0 0 16px;text-align:center;">
    <img src="{THEME_IMG_END}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="主题配图"/>
  </p>

  <p style="font-size:14px;color:#ccc;text-align:center;letter-spacing:8px;margin:24px 0 16px;">· · · · · ·</p>

  <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 8px;line-height:1.6;">
    <span>📖 《书名》</span>
  </p>
  <p style="font-size:14px;color:{BODY};text-align:center;margin:0 0 4px;line-height:1.6;">
    <span>作者 · 读书笔记</span>
  </p>
  <p style="font-size:14px;color:{T2};text-align:center;margin:0 0 24px;line-height:1.8;font-weight:bold;">
    <span>「 一句话总结：核心洞察 」</span>
  </p>

</section>"""


def main():
    print("=" * 50)
    print("微信公众号 - 书名 发布")
    print("=" * 50)

    config = load_config()
    token = get_access_token(config)
    print("\n✓ Token 已获取\n")

    cover_900_path = os.path.join(COVER_DIR, "cover_900x500.jpg")
    if not os.path.exists(cover_900_path):
        print(f"错误: 封面图不存在 {cover_900_path}", file=sys.stderr)
        print("请先运行主题贴图下载与封面裁剪流程", file=sys.stderr)
        sys.exit(1)

    print("上传封面图...")
    cover_mid = upload_cover(token, cover_900_path)

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
