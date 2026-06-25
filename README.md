# wechat-media-writer

微信公众号书评、影评文章自动生成与发布

## 安装

### 方式一：Claude Code Skill（自然语言触发）

```bash
git clone https://github.com/your-username/wechat-media-writer.git ~/.claude/skills/wechat-media-writer
```

安装后直接说：

```
帮我写一篇公众号文章，拆解《人类简史》
发公众号：《肖申克的救赎》影评
书评：《反脆弱》
影评：《霸王别姬》
```

触发词：`写公众号文章`、`发公众号`、`发微信文章`、`公众号草稿`、`书评`、`影评`、`读书拆解`、`wechat publish`

### 方式二：npx 命令行

```bash
npx wechat-media-writer cover "人类简史" "尤瓦尔·赫拉利"
npx wechat-media-writer download books 5
npx wechat-media-writer publish \
  --title "《人类简史》全书深度拆解" \
  --content-file content.html \
  --cover-dir /tmp/wx \
  --book-title "人类简史" \
  --book-author "尤瓦尔·赫拉利" \
  --theme books
```

### 方式三：全局安装

```bash
npm install -g wechat-media-writer
wechat-media-writer cover "人类简史"
```

## 配置

创建 `~/.wechat/config.json`：

```json
{
    "appid": "你的AppID",
    "appsecret": "你的AppSecret"
}
```

access_token 自动缓存在 `~/.wechat/token_cache.json`（2小时有效期）。

## 命令

### `cover` — 获取封面

```bash
npx wechat-media-writer cover <书名/电影名> [作者] [ISBN]
```

按优先级自动从 Google Books → Open Library → 豆瓣 获取封面；
三个数据源均失败时回退到 Pexels 占位图（保证流程不中断）。

### `download` — 下载主题插图

```bash
npx wechat-media-writer download [主题] [数量] [输出目录]
```

主题：`abstract`、`books`、`nature`、`technology`、`business`，默认 `abstract`，数量默认 `5`，目录默认 `/tmp/images`。

### `publish` — 发布文章到微信草稿箱

```bash
npx wechat-media-writer publish --title "标题" --content-file content.html --cover-dir <目录>
```

`publish` 是**完整一键发布**：

1. 检查封面图，缺失则自动获取
2. 检查主题插图，缺失则自动下载
3. 加载微信配置、获取 token
4. 上传封面（永久素材）+ 内容图（uploadimg）
5. 创建草稿

#### 完整参数

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `--title` | 是 | 文章标题 |
| `--content-file` | 是 | HTML 内容文件路径 |
| `--cover-dir` | 是 | 封面和图片目录（自动创建） |
| `--author` | 否 | 文章作者，默认 `读书笔记` |
| `--digest` | 否 | 文章摘要 |
| `--theme` | 否 | 图片主题，默认 `abstract` |
| `--image-count` | 否 | 主题插图数量，默认 `5` |
| `--book-title` | 否 | 书籍标题（封面缺失时自动获取） |
| `--book-author` | 否 | 书籍作者 |
| `--book-isbn` | 否 | 书籍 ISBN |

成功后输出草稿 ID，前往 https://mp.weixin.qq.com 预览发布。

### `help` — 查看帮助

```bash
npx wechat-media-writer help
```

## 项目结构

```
wechat-media-writer/
├── SKILL.md                    # Skill 规范说明
├── README.md                   # 本文件
├── package.json                # npm 包配置
├── bin/
│   └── cli.js                  # CLI 入口
├── scripts/
│   ├── book_cover.py          # 书籍封面获取
│   ├── image_downloader.py    # 主题插图下载（含美学评分挑选封面）
│   ├── wechat_api.py          # 微信 API 封装（token/上传/草稿）
│   ├── publish.py             # 一键发布主脚本（含封面/插图自动补齐）
│   └── install.js             # npm postinstall（检查 Python/Pillow + 注册 Skill）
```

## 发布到 npm

```bash
npm login
npm publish
```

## License

MIT