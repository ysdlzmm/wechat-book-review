#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const SKILL_DIR = path.join(__dirname, '..');
const SCRIPTS_DIR = path.join(SKILL_DIR, 'scripts');

// 检查Python环境
function checkPython() {
  try {
    execSync('python3 --version', { stdio: 'pipe' });
    return 'python3';
  } catch {
    try {
      execSync('python --version', { stdio: 'pipe' });
      return 'python';
    } catch {
      console.error('错误: 需要安装 Python 3');
      console.error('请访问 https://www.python.org/downloads/ 安装');
      process.exit(1);
    }
  }
}

// 检查依赖
function checkDependencies() {
  try {
    execSync('python3 -c "from PIL import Image"', { stdio: 'pipe' });
  } catch {
    console.log('正在安装 Python 依赖...');
    execSync('pip3 install Pillow', { stdio: 'inherit' });
  }
}

// 显示帮助信息
function showHelp() {
  console.log(`
微信公众号书评、影评自动发布工具

用法:
  npx wechat-media-writer <command> [options]

命令:
  cover <书名/电影名> [作者] [ISBN]    获取书籍封面
  download <主题> [数量]                下载主题插图
  publish                               发布文章到微信（封面/插图缺失会自动补齐）
  help                                  显示帮助信息

publish 选项:
  --title <标题>             文章标题（必填）
  --content-file <路径>      HTML 内容文件（必填）
  --cover-dir <目录>         封面和图片目录（必填）
  --author <作者>            文章作者，默认"读书笔记"
  --digest <摘要>            文章摘要
  --theme <主题>             图片主题：abstract/books/nature/technology/business，默认 abstract
  --image-count <数量>       主题插图数量，默认 5
  --book-title <书名>        书籍标题（封面缺失时自动获取）
  --book-author <作者>       书籍作者
  --book-isbn <ISBN>         书籍ISBN

示例:
  npx wechat-media-writer cover "人类简史" "尤瓦尔·赫拉利"
  npx wechat-media-writer download books 5
  npx wechat-media-writer publish \\
    --title "《人类简史》全书深度拆解" \\
    --content-file content.html \\
    --cover-dir /tmp/wx \\
    --book-title "人类简史" \\
    --book-author "尤瓦尔·赫拉利" \\
    --theme books

配置:
  创建 ~/.wechat/config.json:
  {
    "appid": "你的AppID",
    "appsecret": "你的AppSecret"
  }
`);
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === 'help' || command === '--help') {
    showHelp();
    return;
  }

  const python = checkPython();
  checkDependencies();

  switch (command) {
    case 'cover':
      if (args.length < 2) {
        console.error('用法: npx wechat-media-writer cover <书名/电影名> [作者/导演]');
        process.exit(1);
      }
      execSync(`${python} ${path.join(SCRIPTS_DIR, 'book_cover.py')} "${args[1]}" "${args[2] || ''}" "${args[3] || ''}"`, { stdio: 'inherit' });
      break;

    case 'download':
      {
        const theme = args[1] || 'abstract';
        const count = args[2] || '5';
        const outDir = args[3] || '/tmp/images';
        execSync(
          `${python} ${path.join(SCRIPTS_DIR, 'image_downloader.py')} "${theme}" "${outDir}" ${count}`,
          { stdio: 'inherit' }
        );
      }
      break;

    case 'publish':
      {
        const publishArgs = args.slice(1).join(' ');
        execSync(
          `${python} ${path.join(SCRIPTS_DIR, 'publish.py')} ${publishArgs}`,
          { stdio: 'inherit' }
        );
      }
      break;

    default:
      console.error(`未知命令: ${command}`);
      showHelp();
      process.exit(1);
  }
}

main();
