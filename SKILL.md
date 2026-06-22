---
name: wechat-book-review
version: 2.1.0
description: |
    微信公众号读书拆解文章自动生成与发布。7段式独立书评格式，含作者背景、
    逻辑导图、核心论点、批判评析、收获与成长、落地方案、星级评分。
    自动下载主题插图、上传微信、生成HTML排版、发布到草稿箱。
    v2.1.0: 更新标题规范、去除数字编号、优化封面图处理、更新星级评分排版。
triggers:
    - 写公众号文章
    - 发公众号
    - 发微信文章
    - 公众号草稿
    - 书评
    - 读书拆解
    - wechat publish
allowed-tools:
    - Bash
    - Read
    - Write
    - Edit
    - Glob
    - Grep
    - WebSearch
    - WebFetch
    - AskUserQuestion
---

# 微信公众号读书拆解自动发布

## 概述

将书籍拆解文章自动生成精美HTML排版并发布到微信公众号草稿箱。
采用7段式独立社科文学批评者视角，每篇文章配独特主题色和贴合主题的插图。

## 凭证配置

凭证存储在 `~/.wechat/config.json`：

```json
{
    "appid": "你的AppID",
    "appsecret": "你的AppSecret"
}
```

Token 缓存在 `~/.wechat/token_cache.json`（自动管理，2小时有效期）。

## 7段式书评结构

每篇读书拆解文章固定7个章节，**不使用数字编号**，直接以章节标题呈现：

| 序号 | 标题                 | 内容要点                                    |
| ---- | -------------------- | ------------------------------------------- |
| 1    | 作者背景与创作时代   | 作者生平、学术/职业背景、成书时代、写作动机 |
| 2    | 全书完整逻辑思维导图 | 逐章概括核心逻辑线，用框图提炼主线          |
| 3    | 三大颠覆性核心论点   | 选3个最有穿透力的论点，附书中案例           |
| 4    | 批判性客观评析       | 短板、逻辑漏洞、适用边界，不吹捧            |
| 5    | 收获与成长           | 读完能带走的三样东西，个人成长视角          |
| 6    | 现实落地应用方案     | 3-4条可操作建议，具体到执行步骤             |
| 7    | 星级评分与适配人群   | ★评分 + 适合/不适合人群清单                 |

## 主题色规范

每篇文章必须使用**不同于之前所有文章**的主题色组合（主色+强调色）。

### 已用主题色记录

| 书名               | 主色    | 强调色  |
| ------------------ | ------- | ------- |
| 失控               | #3A8F7E | —       |
| 人有人的用处       | #6B7FA5 | —       |
| 系统之美 v1        | #C27A43 | —       |
| 事实               | #4A8B7F | —       |
| 理解媒介           | #8B5E3C | —       |
| 反脆弱             | #B84C3A | —       |
| 一生的旅程         | #2D5F8A | —       |
| 地狱占星师         | #6B2D5B | #9B4D8C |
| 思维方式           | #2D5F3E | #D4A843 |
| 七个习惯           | #2C3E50 | #E67E22 |
| 纳瓦尔宝典         | #1B3A4B | #E07A5F |
| 起床后的黄金一小时 | #382E4C | #F4A261 |
| 系统之美 v2        | #2E5266 | #D4A24C |

### 配色原则

-   主色（T）：深色系，用于标题、强调文字、章节编号
-   强调色（T2）：暖色或亮色，用于论点标题、星标、装饰元素
-   正文色（BODY）：`#555`
-   引用块背景（CBG）：主色的浅色版（加白84%）
-   整体背景：`#FBF8FC`

## 标题规范

标题必须**犀利、抓住洞察、引人入胜**，避免平铺直叙。

### 标题公式

**《书名》全书深度拆解：[犀利洞察/颠覆认知的结论]**

### 示例

| 书名       | 平庸标题             | 犀利标题                                                                            |
| ---------- | -------------------- | ----------------------------------------------------------------------------------- |
| 思维方式   | 《思维方式》读书笔记 | 稻盛和夫《思维方式》全书深度拆解：他创办了两家世界500强，却说能力只占三分之一的分数 |
| 反脆弱     | 《反脆弱》书评       | 《反脆弱》全书深度拆解：为什么"杀不死你的"未必让你更强，除非你懂得这个机制          |
| 系统之美   | 《系统之美》拆解     | 《系统之美》全书深度拆解：99%的人困在系统里，只有1%的人看懂了这3个杠杆点            |
| 油炸绿番茄 | 《油炸绿番茄》书评   | 《油炸绿番茄》全书深度拆解：一个南方小镇的咖啡馆，藏着关于女性勇气的终极秘密        |

### 标题要求

1. **必须包含书名**，格式为《书名》
2. **必须有"全书深度拆解"字样**（保持系列一致性）
3. **冒号后必须是犀利洞察**——一句话点出这本书最颠覆/最核心的价值
4. **字数控制在25-40字**——太短没信息量，太长显示不全
5. **避免形容词堆砌**——不要"震撼！深刻！必读！"，要具体结论

## HTML排版规范

### 基本结构

```html
<section
    style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#333;background:#FBF8FC;"
>
    <!-- 头部 -->
    <p style="font-size:12px;color:{T2};text-align:center;letter-spacing:4px;margin:24px 0 8px;line-height:3em;">
        <span>📖 读书拆解</span>
    </p>
    <p style="font-size:22px;font-weight:bold;color:{T};text-align:center;margin:0 0 6px;line-height:1.5;">
        <span>《书名》全书深度拆解</span>
    </p>
    <p style="font-size:14px;color:#999;text-align:center;margin:0 0 20px;line-height:3em;">
        <span>副标题（一句话点睛）</span>
    </p>

    <!-- 书籍封面图（第一张图，使用书籍原封面） -->
    <p style="margin:0 0 20px;text-align:center;">
        <img src="{BOOK_COVER_URL}" style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;" alt="《书名》封面" />
    </p>

    <!-- 章节（无数字编号，直接标题） -->
    <p style="font-size:18px;font-weight:bold;color:{T};text-align:center;margin:0 0 16px;line-height:1em;">
        <span>作者背景与创作时代</span>
    </p>
    <p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
        <span>正文段落。所有段落必须有 text-indent:2em。</span>
    </p>

    <!-- 引用块 -->
    <p
        style="font-size:17px;line-height:1.9;color:rgb(T_R,T_G,T_B);font-weight:bold;text-indent:2em;margin:0 0 20px;padding:14px 18px;background:rgb(CBG);border-radius:8px;"
    >
        <span>金句或核心观点引用。</span>
    </p>

    <!-- 分隔符（章节之间） -->
    <p style="font-size:14px;color:#ccc;text-align:center;letter-spacing:8px;margin:20px 0;">· · · · · ·</p>
</section>
```

### 关键排版规则

1. **所有正文段落必须有 `text-indent:2em`** — 首行缩进
2. **图片URL必须用完整的 `mmbiz.qpic.cn` 硬编码URL** — 不用模板变量
3. **`<img>` 必须包裹在 `<p>` 中**，且 `style="width:100%;display:block;border-radius:4px;"`
4. **行高统一 `line-height:2`** — 阅读舒适
5. **引用块用 `<p>` + `background` + `border-radius:8px`** — 不是 `<blockquote>`
6. **章节标题不使用数字编号** — 直接用"作者背景与创作时代"，不用"壹"
7. **强调文字用 `<strong style="color:{T};">`** — 不是加粗或改色
8. **星标用 `<span>★★★★☆</span>`** — `font-size:28px;color:{T2}`
9. **每篇文章只在一个 `<section>` 内** — 不嵌套多个 section
10. **第一张图必须是书籍封面** — 使用书籍原封面图，居中显示，max-width:600px

## 图片工作流

### 第一步：获取书籍封面图

**书评文章的第一张图必须是书籍原封面**，需要特殊处理：

```python
# 书籍封面图需要从网上获取或用户提供
# 封面图尺寸要求：宽度建议600px，高度按比例缩放
# 微信文章内图片最大宽度为600px，封面图应居中显示

# 封面图HTML格式（区别于普通内容图的100%宽度）：
# style="width:100%;max-width:600px;display:block;margin:0 auto;border-radius:4px;"
```

### 第二步：下载主题插图

推荐使用 Pexels CDN（Unsplash 直链大量 404）：

```python
import urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Pexels CDN 格式：https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg
url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1080"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = urllib.request.urlopen(req, context=ctx, timeout=15).read()
```

每篇文章需要 5-6 张内容图 + 1张书籍封面图 + 1张封面图（900x500用于公众号封面）。

### 第二步：制作封面图

```python
from PIL import Image
img = Image.open("source.jpg")
w, h = img.size
target_ratio = 900 / 500
if w / h > target_ratio:
    new_w = int(h * target_ratio)
    left = (w - new_w) // 2
    img = img.crop((left, 0, left + new_w, h))
else:
    new_h = int(w / target_ratio)
    top = (h - new_h) // 2
    img = img.crop((0, top, w, top + new_h))
img = img.resize((900, 500), Image.LANCZOS)
img.save("cover_900x500.jpg", "JPEG", quality=85)
```

### 第三步：上传到微信

```python
# 封面 → add_material（永久素材，返回 media_id 用于 thumb_media_id）
_wx_upload(f"cgi-bin/material/add_material?access_token={token}&type=image", "cover_900x500.jpg")
# 返回 {"media_id": "D2K...", "url": "http://mmbiz.qpic.cn/..."}

# 内容图 → uploadimg（返回 mmbiz URL 用于文章内嵌）
_wx_upload(f"cgi-bin/media/uploadimg?access_token={token}", "image.jpg")
# 返回 {"url": "http://mmbiz.qpic.cn/..."}
```

### 第四步：硬编码 URL

将上传后的 media_id 和 mmbiz URL **硬编码到发布脚本中**，不用模板变量。
这是因为微信图片URL有时效性，硬编码已验证的URL最可靠。

## 微信 API 集成

### DNS 绕行

微信 API 在某些网络环境下 DNS 会被劫持。用 `dig` 通过外部 DNS 解析真实 IP：

```python
def _resolve_wx_ip():
    import subprocess
    r = subprocess.run(
        ["dig", "+short", "api.weixin.qq.com", "@8.8.8.8"],
        capture_output=True, text=True, timeout=5
    )
    ips = [ip.strip() for ip in r.stdout.strip().split("\n") if ip.strip()]
    return ips[0] if ips else "api.weixin.qq.com"
```

### SSL 连接

用真实 IP 连接但 SNI 使用域名，保证 SSL 证书验证通过：

```python
def _wx_request(path, method="GET", data=None, headers=None, timeout=30):
    ctx = ssl.create_default_context()
    sock = socket.create_connection((_WX_REAL_IP, 443), timeout=timeout)
    ssl_sock = ctx.wrap_socket(sock, server_hostname="api.weixin.qq.com")
    conn = http.client.HTTPSConnection("api.weixin.qq.com", timeout=timeout, context=ctx)
    conn.sock = ssl_sock
    conn.request(method, f"/{path}", body=data, headers=req_headers)
    resp = conn.getresponse()
    body = resp.read().decode()
    conn.close()
    return resp.status, body
```

### Multipart 上传

`uploadimg` 和 `add_material` 需要 multipart/form-data：

```python
def _wx_upload(path, filepath, extra_fields=None, timeout=60):
    boundary = uuid.uuid4().hex
    body_parts = []
    if extra_fields:
        for k, v in extra_fields.items():
            body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    with open(filepath, "rb") as f:
        file_data = f.read()
    body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"media\"; filename=\"{filename}\"\r\nContent-Type: {mime_type}\r\n\r\n".encode())
    body_parts.append(file_data)
    body_parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(body_parts)
    # 发送...
```

### API 列表

| API                             | 用途                 | 方法           |
| ------------------------------- | -------------------- | -------------- |
| `cgi-bin/token`                 | 获取 access_token    | GET            |
| `cgi-bin/material/add_material` | 上传永久素材（封面） | POST multipart |
| `cgi-bin/media/uploadimg`       | 上传文章内图片       | POST multipart |
| `cgi-bin/draft/add`             | 创建草稿             | POST JSON      |

### 错误处理

| 错误码 | 含义               | 处理                |
| ------ | ------------------ | ------------------- |
| 40001  | token 无效         | 重新获取 token      |
| 40007  | invalid media_id   | 重新上传封面图      |
| 40164  | IP 不在白名单      | 提示用户添加 IP     |
| 41005  | media data missing | 检查 multipart 格式 |
| 45009  | 频率限制           | 等待后重试          |

## 完整发布流程

### 1. 确认书籍信息

向用户确认：书名、作者、是否需要特定主题色。

### 2. 下载主题插图

根据书籍主题选择贴合的图片（自然、复杂、网络、静谧等）。
推荐来源：Pexels CDN（比 Unsplash 直链更稳定）。

### 3. 上传图片到微信

-   封面 → `add_material` 获取 `media_id`
-   内容图 → `uploadimg` 获取 `mmbiz` URL
-   所有 URL 保存到 `upload_result.json`

### 4. 撰写7段式内容

以独立社科文学批评者视角，基于真实研究撰写原创内容。
不抄袭参考文章，每个论点附书中案例。

### 5. 生成发布脚本

参考 `references/publish_template.py`，将：

-   主题色变量（T, T2, BODY, CBG）
-   硬编码图片 URL
-   7段式 HTML 内容
-   标题、摘要

写入完整 Python 脚本。

### 6. 执行发布

```bash
python3 /tmp/publish_xxx.py
```

成功后输出草稿 ID，提示用户去 https://mp.weixin.qq.com 预览。

## 内容写作指南

### 角色：独立社科文学批评者

-   不吹捧、不带货、不写软文
-   有观点、有批判、有温度
-   每个论点必须有书中案例支撑
-   批判章节至少列出4个短板
-   星级评分诚实（3-4星是常态，5星极少）

### 内容来源

-   Wikipedia / 豆瓣：作者背景、书籍基本信息
-   书评 / 学术论文：交叉验证核心论点
-   原书引用：逻辑导图和论点章节必须引用原书
-   **不抄袭参考文章**：所有内容原创，基于研究重新组织

### 字数参考

| 章节       | 字数          |
| ---------- | ------------- |
| 作者背景   | 400-600       |
| 逻辑导图   | 600-800       |
| 三大论点   | 1200-1800     |
| 批判评析   | 600-800       |
| 收获与成长 | 600-800       |
| 落地方案   | 600-800       |
| 星级评分   | 400-500       |
| **总计**   | **4000-6000** |

## 星级评分与适配人群排版规范

星级评分部分必须按照以下格式排版，**不使用壹贰叁编号**：

```html
<p style="font-size:14px;color:#ccc;text-align:center;letter-spacing:8px;margin:20px 0;">· · · · · ·</p>

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
    <span>为什么给X星？简要说明评分理由，诚实评价，3-4星是常态，5星极少。</span>
</p>

<p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 8px;text-indent:2em;">
    <strong style="color:{T};">适合人群：</strong>
</p>
<p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>✓ 创业者/管理者——具体理由<br />✓ 陷入职业倦怠期的人——具体理由<br />✓ 对某领域感兴趣的读者——具体理由</span>
</p>

<p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 8px;text-indent:2em;">
    <strong style="color:{T};">不适合人群：</strong>
</p>
<p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;text-indent:2em;">
    <span>✗ 已读过类似书籍的人——内容高度重复<br />✗ 讨厌某种风格的人——具体理由<br />✗ 寻找其他类型内容的人——具体理由</span>
</p>
```

### 评分格式要求

1. **星级显示**：`font-size:28px;color:{T2}`，居中
2. **分数显示**：`4 / 5 星`，在星标下方
3. **评分理由**：1-2句话解释为什么给这个分数
4. **适合人群**：用 ✓ 标记，每条用——连接理由
5. **不适合人群**：用 ✗ 标记，每条用——连接理由
6. **不要直接放链接**——所有内容用文案表达
