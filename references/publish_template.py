#!/usr/bin/env python3
"""
微信公众号读书拆解发布脚本模板
替换以下变量后直接使用：
  - COVER_MID: 封面 media_id（通过 wechat_publish.py --upload-dir 获取）
  - IMG_xxx: 内容图片 mmbiz URL
  - T / T2: 主题色（主色 / 强调色）
  - html: 7段式文章 HTML 内容
  - title / digest: 标题和摘要
"""

import json, os, sys, time, ssl, socket, subprocess, http.client

CONFIG_PATH = os.path.expanduser("~/.wechat/config.json")
TOKEN_CACHE_PATH = os.path.expanduser("~/.wechat/token_cache.json")
WX_API_HOST = "api.weixin.qq.com"


def _resolve_wx_ip():
    try:
        r = subprocess.run(
            ["dig", "+short", WX_API_HOST, "@8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        ips = [
            ip.strip()
            for ip in r.stdout.strip().split("\n")
            if ip.strip() and not ip.startswith(";")
        ]
        return ips[0] if ips else WX_API_HOST
    except:
        return WX_API_HOST


_WX_REAL_IP = _resolve_wx_ip()


def _wx_request(path, method="GET", data=None, headers=None, timeout=30):
    ctx = ssl.create_default_context()
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    sock = socket.create_connection((_WX_REAL_IP, 443), timeout=timeout)
    ssl_sock = ctx.wrap_socket(sock, server_hostname=WX_API_HOST)
    conn = http.client.HTTPSConnection(WX_API_HOST, timeout=timeout, context=ctx)
    conn.sock = ssl_sock
    req_h = {"Host": WX_API_HOST}
    if headers:
        req_h.update(headers)
    conn.request(method, f"/{path}", body=data, headers=req_h)
    resp = conn.getresponse()
    body = resp.read().decode()
    conn.close()
    return resp.status, body


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_access_token(config):
    if os.path.exists(TOKEN_CACHE_PATH):
        try:
            with open(TOKEN_CACHE_PATH, "r") as f:
                cache = json.load(f)
            if cache.get("expires_at", 0) > time.time() + 300:
                return cache["access_token"]
        except:
            pass
    status, body = _wx_request(
        f"cgi-bin/token?grant_type=client_credential&appid={config['appid']}&secret={config['appsecret']}",
        timeout=15,
    )
    data = json.loads(body)
    if "errcode" in data:
        print(f"获取token失败: {data}", file=sys.stderr)
        sys.exit(1)
    token = data["access_token"]
    exp = data.get("expires_in", 7200)
    os.makedirs(os.path.dirname(TOKEN_CACHE_PATH), exist_ok=True)
    with open(TOKEN_CACHE_PATH, "w") as f:
        json.dump({"access_token": token, "expires_at": time.time() + exp}, f)
    return token


def create_draft(token, title, author, digest, content_html, thumb_media_id):
    article = {
        "title": title,
        "author": author,
        "digest": digest or "",
        "content": content_html,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    payload = json.dumps({"articles": [article]}, ensure_ascii=False).encode()
    try:
        s, b = _wx_request(
            f"cgi-bin/draft/add?access_token={token}",
            method="POST",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        r = json.loads(b)
    except Exception as e:
        print(f"创建草稿失败: {e}", file=sys.stderr)
        sys.exit(1)
    if "errcode" in r:
        print(f"创建草稿失败: [{r['errcode']}] {r.get('errmsg', '')}", file=sys.stderr)
        sys.exit(1)
    return r["media_id"]


# ========== 替换以下内容 ==========

# 封面 media_id（通过 wechat_publish.py --upload-dir 上传后获取）
COVER_MID = "REPLACE_WITH_COVER_MEDIA_ID"

# 内容图片 URL（通过 wechat_publish.py --upload-dir 上传后获取）
IMG_BOOK_COVER = (
    "http://mmbiz.qpic.cn/REPLACE_WITH_BOOK_COVER_URL"  # 书籍封面图（第一张图）
)
IMG_1 = "http://mmbiz.qpic.cn/REPLACE_WITH_IMG_1_URL"
IMG_2 = "http://mmbiz.qpic.cn/REPLACE_WITH_IMG_2_URL"
IMG_3 = "http://mmbiz.qpic.cn/REPLACE_WITH_IMG_3_URL"
IMG_4 = "http://mmbiz.qpic.cn/REPLACE_WITH_IMG_4_URL"
IMG_5 = "http://mmbiz.qpic.cn/REPLACE_WITH_IMG_5_URL"

# 主题色：主色（深色）+ 强调色（暖/亮色）
T = "#2E5266"  # 主色
T2 = "#D4A24C"  # 强调色
BODY = "#555"  # 正文色
CBG = "#F0EDE5"  # 引用块背景

# 文章 HTML 内容（7段式，无数字编号）
html = f"""<section style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#333;background:#FBF8FC;">

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
    <img src="{IMG_BOOK_COVER}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="《书名》封面"/>
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

  <!-- 其他章节（全书完整逻辑思维导图、三大颠覆性核心论点、批判性客观评析、收获与成长、现实落地应用方案） -->

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
    title = "书名拆解：副标题"
    author = "读书笔记"
    digest = "摘要文本，不超过120字。"

    print("=" * 50)
    print("微信公众号 - 书名 发布")
    print("=" * 50)

    config = load_config()
    token = get_access_token(config)
    print("\nToken 已获取\n")

    print("发布草稿...")
    draft_id = create_draft(token, title, author, digest, html, COVER_MID)

    print("\n" + "=" * 50)
    print("发布成功!")
    print("=" * 50)
    print(f"标题:   {title}")
    print(f"作者:   {author}")
    print(f"草稿ID: {draft_id}")
    print(f"\n请前往微信公众平台查看草稿:")
    print(f"https://mp.weixin.qq.com")


if __name__ == "__main__":
    main()
