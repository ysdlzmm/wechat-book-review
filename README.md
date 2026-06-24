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
npx wechat-media-writer cover "肖申克的救赎" "弗兰克·德拉邦特"
npx wechat-media-writer publish --title "标题" --content-file content.html --cover-dir /tmp/output
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

## 命令

### 获取封面

```bash
npx wechat-media-writer cover <书名/电影名> [作者/导演]
```

自动从 Google Books、Open Library、豆瓣获取封面。

### 下载主题插图

```bash
npx wechat-media-writer download [主题] [数量]
```

主题：`nature`、`technology`、`abstract`、`books`、`movies`、`business`

### 发布文章

```bash
npx wechat-media-writer publish --title "标题" --content-file content.html --cover-dir /tmp/output
```

### 查看帮助

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
│   ├── book_cover.py          # 封面获取（书/影）
│   ├── image_downloader.py    # 图片下载
│   ├── wechat_api.py          # 微信API封装
│   ├── publish.py             # 完整发布脚本
│   └── install.js             # npm postinstall
└── references/
    └── publish_template.py    # 发布脚本模板
```

## 发布到 npm

```bash
npm login
npm publish
```

## License

MIT
