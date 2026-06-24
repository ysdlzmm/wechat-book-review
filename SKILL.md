---
name: wechat-book-review
version: 2.2.0
description: |
    微信公众号读书拆解文章自动生成与发布。7段式独立书评格式，含作者背景、
    逻辑导图、核心论点、批判评析、收获与成长、落地方案、星级评分。
    自动下载主题插图、上传微信、生成HTML排版、发布到草稿箱。
    v2.2.0: 重构结构，代码提取到独立模块，SKILL.md仅保留规范说明。
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

## 项目结构

```
wechat-skill/
├── SKILL.md                    # 本文件 - 规范说明
├── scripts/
│   ├── book_cover.py          # 书籍封面获取模块
│   ├── image_downloader.py    # 图片下载模块
│   ├── wechat_api.py          # 微信API封装
│   └── publish.py             # 完整发布脚本
└── references/
    └── publish_template.py    # 发布脚本模板
```

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
| 1    | 先搞懂写书的这个人   | 作者生平、学术/职业背景、成书时代、写作动机 |
| 2    | 全书脉络 | 逐章概括核心逻辑线，用框图提炼主线          |
| 3    | 三个颠覆认知的真相  | 选3个最有穿透力的论点，附书中案例           |
| 4    | 这本书的短板，不吐不快       | 根据书籍实际情况灵活呈现：有短板则评短板，无明显漏洞则评适用边界或争议点，不强制批判             |
| 5    | 读完真正留下的东西           | 读完能带走的三样东西，个人成长视角          |
| 6    | 四条拿来就用的行动项     | 3-4条可操作建议，具体到执行步骤             |
| 7    | 值不值得花时间读   | ★评分 + 适合/不适合人群清单                 |


## 主题色规范

每篇文章随机生成主题色组合（主色+强调色），确保视觉多样性。

### 生成规则

1. **主色（T）**：HSL色彩空间，H随机（0-360），S 40-60%，L 30-45%（深色系）
2. **强调色（T2）**：与主色H值相差120-180度（形成对比），S 50-70%，L 45-55%
3. **禁止组合**：主色与强调色明度差 < 15%时重新生成

## 标题规范

标题必须**犀利、抓住洞察、引人入胜**，避免平铺直叙。

### 标题结构

**[前半模板]：[犀利洞察/颠覆认知的结论]**

### 前半模板库（随机选1个）

《书名》全书深度拆解
拆完《书名》，我有话说
《书名》到底写了什么
花X小时读完《书名》
关于《书名》你该知道的一切
《书名》这本书，拆透了
《书名》的真相
我为什么建议你读《书名》

### 后半部分

冒号后必须是**犀利洞察**——一句话点出这本书最颠覆/最核心的价值。

### 标题要求

1. **必须包含书名**，格式为《书名》
2. **前半部分随机选择模板**——保持系列多样性，避免千篇一律
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

**书评文章的第一张图必须是书籍原封面**

使用 `scripts/book_cover.py` 模块自动获取：

```python
from book_cover import fetch_book_cover, download_and_process_cover

# 自动获取封面URL（Google Books -> Open Library -> 豆瓣）
cover_url = fetch_book_cover("书名", "作者", "ISBN")

# 下载并处理（生成600px文章封面 + 900x500公众号封面）
if cover_url:
    cover_path, cover_900_path = download_and_process_cover(cover_url, "/tmp/output")
```

**封面尺寸要求**：
- 文章内封面：宽度 600px，高度按比例缩放
- 公众号封面：900x500px（用于文章列表展示）

### 第二步：下载主题插图

使用 `scripts/image_downloader.py` 下载：

```python
from image_downloader import download_theme_images

# 根据主题下载5张插图
urls = download_theme_images("nature", "/tmp/images", count=5)
```

每篇文章需要 5-6 张内容图 + 1张书籍封面图 + 1张封面图（900x500用于公众号封面）。

### 第三步：上传图片到微信

使用 `scripts/wechat_api.py` 上传：

```python
from wechat_api import upload_cover, upload_content_image

# 上传封面（永久素材）
cover_mid = upload_cover(token, "cover_900x500.jpg")

# 上传内容图（返回mmbiz URL）
img_url = upload_content_image(token, "image.jpg")
```

### 第四步：硬编码 URL

将上传后的 media_id 和 mmbiz URL **硬编码到发布脚本中**，不用模板变量。
这是因为微信图片URL有时效性，硬编码已验证的URL最可靠。

## 微信 API 集成

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

### 2. 获取封面图

```bash
python3 scripts/book_cover.py "书名" "作者" "ISBN"
```

### 3. 下载主题插图

```bash
python3 -c "from scripts.image_downloader import download_theme_images; download_theme_images('theme', '/tmp/images')"
```

### 4. 上传图片到微信

```bash
python3 scripts/publish.py --upload-dir /tmp/images
```

### 5. 撰写7段式内容

以独立社科文学批评者视角，基于真实研究撰写原创内容。
不抄袭参考文章，每个论点附书中案例。

### 6. 生成发布脚本

参考 `references/publish_template.py`，将：

-   主题色变量（T, T2, BODY, CBG）
-   硬编码图片 URL
-   7段式 HTML 内容
-   标题、摘要

写入完整 Python 脚本。

### 7. 执行发布

```bash
python3 scripts/publish.py --title "标题" --content-file content.html --cover-dir /tmp/images
```

成功后输出草稿 ID，提示用户去 https://mp.weixin.qq.com 预览。

## 内容写作指南

### 角色：独立社科文学批评者
-   不吹捧、不带货、不写软文
-   有观点、有温度
-   每个论点必须有书中案例支撑
-   批判章节：根据书籍实际情况灵活处理，有明显短板则评短板，无明显问题则评适用边界、争议点或时代局限，不强制批判
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
<p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;padding-left:2em;">
    <span>✓ 创业者/管理者——具体理由<br />✓ 陷入职业倦怠期的人——具体理由<br />✓ 对某领域感兴趣的读者——具体理由</span>
</p>

<p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 8px;text-indent:2em;">
    <strong style="color:{T};">不适合人群：</strong>
</p>
<p style="font-size:16px;line-height:2;color:{BODY};margin:0 0 16px;padding-left:2em;">
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
