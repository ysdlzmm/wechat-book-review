#!/usr/bin/env python3
"""
微信公众号 API 封装模块
支持：获取token、上传图片、创建草稿
"""

import http.client
import json
import mimetypes
import os
import socket
import ssl
import subprocess
import sys
import time
import uuid

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


if __name__ == "__main__":
    print("微信API模块 - 请作为模块导入使用")
