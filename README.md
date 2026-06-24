# 微信公众号读书拆解自动发布

将书籍拆解文章自动生成精美HTML排版并发布到微信公众号草稿箱。

## 使用示例

### 1. 安装到本地

```bash
# 克隆仓库
git clone https://github.com/your-username/wechat-skill.git
cd wechat-skill

# 安装依赖
pip install Pillow
```

### 2. 配置凭证

创建 `~/.wechat/config.json`：

```json
{
    "appid": "你的AppID",
    "appsecret": "你的AppSecret"
}
```

### 3. 触发 Skill

#### Claude Code

将目录放入 `~/.claude/skills/`：

```bash
cp -r wechat-skill ~/.claude/skills/wechat-book-review
```

在对话中使用触发词自动加载：

```
帮我写一篇公众号文章，拆解《人类简史》
```

触发词：`写公众号文章`、`发公众号`、`发微信文章`、`公众号草稿`、`书评`、`读书拆解`、`wechat publish`

#### Cursor / Windsurf / 其他 AI IDE

将目录放入项目根目录的 `.skills/` 或 `.cursorrules` 中引用：

```markdown
参考 ./wechat-skill/SKILL.md 中的规范
```

#### 通用命令行

直接调用脚本，无需任何 CLI 工具：

```bash
# 获取封面
python3 scripts/book_cover.py "人类简史" "尤瓦尔·赫拉利"

# 发布文章
python3 scripts/publish.py \
    --title "《人类简史》全书深度拆解" \
    --content-file content.html \
    --cover-dir /tmp/book_output
```

## 项目结构

```
wechat-skill/
├── SKILL.md                    # 规范说明文档
├── README.md                   # 本文件
├── scripts/
│   ├── book_cover.py          # 书籍封面获取模块
│   ├── image_downloader.py    # 图片下载模块
│   ├── wechat_api.py          # 微信API封装
│   └── publish.py             # 完整发布脚本
└── references/
    └── publish_template.py    # 发布脚本模板
```

## 快速开始

### 1. 配置凭证

创建 `~/.wechat/config.json`：

```json
{
    "appid": "你的AppID",
    "appsecret": "你的AppSecret"
}
```

### 2. 获取书籍封面

```bash
python3 scripts/book_cover.py "书名" "作者" "ISBN"
```

自动从 Google Books、Open Library、豆瓣获取封面，生成：
- `book_cover.jpg` - 文章内封面（600px宽）
- `cover_900x500.jpg` - 公众号封面（900x500px）

### 3. 下载主题插图

```python
from scripts.image_downloader import download_theme_images

# 可选主题: nature, technology, abstract, books, business
urls = download_theme_images("books", "/tmp/images", count=5)
```

### 4. 撰写7段式内容

按照 SKILL.md 中的规范撰写HTML内容，保存为 `content.html`

### 5. 发布到微信

```bash
python3 scripts/publish.py \
    --title "《书名》全书深度拆解：犀利洞察" \
    --author "读书笔记" \
    --digest "摘要文本" \
    --content-file content.html \
    --cover-dir /tmp/book_output
```

## 模块说明

### book_cover.py

书籍封面获取模块，支持三种来源：
- Google Books API（推荐）
- Open Library API（需ISBN）
- 豆瓣搜索（备用）

### image_downloader.py

图片下载模块，支持：
- Pexels CDN 图片下载
- 按主题批量下载

### wechat_api.py

微信公众号API封装：
- access_token 管理（自动缓存）
- 图片上传（封面/内容图）
- 草稿创建

### publish.py

完整发布脚本，整合所有模块。

## 参考资源

- [SKILL.md](SKILL.md) - 完整规范说明
- [references/publish_template.py](references/publish_template.py) - 发布脚本模板
