#!/usr/bin/env python3
"""
微信公众号通用发布脚本
支持：获取token、上传封面、上传内容图片、创建草稿
用法：
  python3 wechat_publish.py --title "标题" --author "作者" --digest "摘要" \
    --content-html "<section>...</section>" --cover-image /path/to/cover.jpg
  或从文件读取：
  python3 wechat_publish.py --title "标题" --content-file content.html --cover-image cover.jpg
"""

import argparse
import json
import os
import sys
import time
import ssl
import socket
import subprocess
import http.client
import mimetypes
import uuid
import tempfile

CONFIG_PATH = os.path.expanduser("~/.wechat/config.json")
TOKEN_CACHE_PATH = os.path.expanduser("~/.wechat/token_cache.json")
WX_API_HOST = "api.weixin.qq.com"


def _resolve_wx_ip():
    """通过外部DNS解析微信API真实IP，绕过本地DNS劫持"""
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
    except Exception:
        return WX_API_HOST


_WX_REAL_IP = _resolve_wx_ip()


def _wx_request(path, method="GET", data=None, headers=None, timeout=30):
    """用真实IP直连微信API，SNI用域名保证SSL验证通过"""
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


def _wx_upload(path, filepath, extra_fields=None, timeout=60):
    """multipart/form-data 上传文件到微信"""
    ctx = ssl.create_default_context()
    sock = socket.create_connection((_WX_REAL_IP, 443), timeout=timeout)
    ssl_sock = ctx.wrap_socket(sock, server_hostname=WX_API_HOST)
    conn = http.client.HTTPSConnection(WX_API_HOST, timeout=timeout, context=ctx)
    conn.sock = ssl_sock

    boundary = uuid.uuid4().hex
    body_parts = []

    if extra_fields:
        for k, v in extra_fields.items():
            body_parts.append(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
            )

    with open(filepath, "rb") as f:
        file_data = f.read()
    filename = os.path.basename(filepath)
    mime_type = mimetypes.guess_type(filepath)[0] or "image/jpeg"
    body_parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="media"; filename="{filename}"\r\nContent-Type: {mime_type}\r\n\r\n'.encode()
    )
    body_parts.append(file_data)
    body_parts.append(f"\r\n--{boundary}--\r\n".encode())

    body = b"".join(body_parts)
    req_headers = {
        "Host": WX_API_HOST,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    conn.request("POST", f"/{path}", body=body, headers=req_headers)
    resp = conn.getresponse()
    resp_body = resp.read().decode()
    conn.close()
    return resp.status, resp_body


def load_config():
    """加载微信配置"""
    if not os.path.exists(CONFIG_PATH):
        print(f"错误: 配置文件不存在 {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def get_access_token(config):
    """获取 access_token，带缓存（提前5分钟刷新）"""
    if os.path.exists(TOKEN_CACHE_PATH):
        try:
            with open(TOKEN_CACHE_PATH, "r") as f:
                cache = json.load(f)
            if cache.get("expires_at", 0) > time.time() + 300:
                return cache["access_token"]
        except (json.JSONDecodeError, KeyError):
            pass

    status, body = _wx_request(
        f"cgi-bin/token?grant_type=client_credential&appid={config['appid']}&secret={config['appsecret']}",
        timeout=15,
    )
    data = json.loads(body)
    if "errcode" in data:
        print(
            f"获取token失败: [{data['errcode']}] {data.get('errmsg', '')}",
            file=sys.stderr,
        )
        sys.exit(1)

    token = data["access_token"]
    expires_in = data.get("expires_in", 7200)
    os.makedirs(os.path.dirname(TOKEN_CACHE_PATH), exist_ok=True)
    with open(TOKEN_CACHE_PATH, "w") as f:
        json.dump({"access_token": token, "expires_at": time.time() + expires_in}, f)
    return token


def upload_cover(token, image_path):
    """上传封面图（永久素材），返回 media_id"""
    if not os.path.exists(image_path):
        print(f"错误: 封面图不存在 {image_path}", file=sys.stderr)
        sys.exit(1)

    status, body = _wx_upload(
        f"cgi-bin/material/add_material?access_token={token}&type=image",
        image_path,
    )
    result = json.loads(body)
    if "errcode" in result:
        print(
            f"封面上传失败: [{result['errcode']}] {result.get('errmsg', '')}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"封面上传成功: media_id={result['media_id']}")
    return result["media_id"]


def upload_content_image(token, image_path):
    """上传内容图，返回 mmbiz URL"""
    if not os.path.exists(image_path):
        print(f"错误: 图片不存在 {image_path}", file=sys.stderr)
        return None

    status, body = _wx_upload(
        f"cgi-bin/media/uploadimg?access_token={token}",
        image_path,
    )
    result = json.loads(body)
    if "url" not in result:
        print(f"图片上传失败: {body[:200]}", file=sys.stderr)
        return None

    print(f"  ✓ {os.path.basename(image_path)}: {result['url']}")
    return result["url"]


def upload_all_images(token, image_dir, cover_name="cover_900x500.jpg"):
    """批量上传图片目录中的所有图片"""
    result = {"cover_mid": "", "book_cover": "", "urls": {}}

    # 上传公众号封面图（900x500）
    cover_path = os.path.join(image_dir, cover_name)
    if os.path.exists(cover_path):
        result["cover_mid"] = upload_cover(token, cover_path)
    else:
        print(f"警告: 封面图不存在 {cover_path}", file=sys.stderr)

    # 上传内容图
    print("\n--- 上传内容图片 ---")
    for fname in sorted(os.listdir(image_dir)):
        if fname == cover_name or not fname.endswith((".jpg", ".jpeg", ".png")):
            continue
        fpath = os.path.join(image_dir, fname)
        name = os.path.splitext(fname)[0]
        url = upload_content_image(token, fpath)
        if url:
            result["urls"][name] = url

    # 识别书籍封面图（如果有 book_cover.jpg 或类似命名）
    book_cover_candidates = [
        "book_cover.jpg",
        "book_cover.jpeg",
        "book_cover.png",
        "book.jpg",
    ]
    for candidate in book_cover_candidates:
        candidate_path = os.path.join(image_dir, candidate)
        if os.path.exists(candidate_path):
            url = upload_content_image(token, candidate_path)
            if url:
                result["book_cover"] = url
                print(f"  ✓ 书籍封面图: {url}")
            break

    # 保存结果
    result_path = os.path.join(image_dir, "upload_result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n已保存 {result_path}")
    return result


def create_draft(token, title, author, digest, content_html, thumb_media_id):
    """创建草稿"""
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

    status, body = _wx_request(
        f"cgi-bin/draft/add?access_token={token}",
        method="POST",
        data=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    result = json.loads(body)
    if "errcode" in result:
        print(
            f"创建草稿失败: [{result['errcode']}] {result.get('errmsg', '')}",
            file=sys.stderr,
        )
        sys.exit(1)
    return result["media_id"]


def main():
    parser = argparse.ArgumentParser(description="微信公众号草稿箱发布工具")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--author", default="读书笔记", help="作者名称")
    parser.add_argument("--digest", default="", help="文章摘要")
    parser.add_argument("--content-html", default="", help="HTML 格式文章正文")
    parser.add_argument("--content-file", default="", help="从文件读取 HTML 内容")
    parser.add_argument("--cover-image", default="", help="封面图路径")
    parser.add_argument("--upload-dir", default="", help="批量上传目录中的图片")
    args = parser.parse_args()

    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            args.content_html = f.read()
    if not args.content_html and not args.upload_dir:
        print(
            "错误: 必须提供 --content-html / --content-file 或 --upload-dir",
            file=sys.stderr,
        )
        sys.exit(1)

    config = load_config()
    token = get_access_token(config)
    print(f"Token 已获取: {token[:20]}...")

    if args.upload_dir:
        result = upload_all_images(token, args.upload_dir)
        print(f"\n封面 media_id: {result['cover_mid']}")
        print(f"内容图片: {len(result['urls'])} 张")
        return

    # 单篇发布模式
    print("\n" + "=" * 50)
    print("微信公众号草稿箱发布")
    print("=" * 50)

    cover_mid = upload_cover(token, args.cover_image) if args.cover_image else ""
    if not cover_mid:
        print("错误: 需要封面图 media_id", file=sys.stderr)
        sys.exit(1)

    draft_id = create_draft(
        token, args.title, args.author, args.digest, args.content_html, cover_mid
    )

    print("\n发布成功!")
    print(f"标题:   {args.title}")
    print(f"作者:   {args.author}")
    print(f"草稿ID: {draft_id}")
    print(f"\nhttps://mp.weixin.qq.com")


if __name__ == "__main__":
    main()
