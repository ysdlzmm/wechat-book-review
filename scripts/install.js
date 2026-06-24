#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const PKG_ROOT = path.resolve(__dirname, '..');
const HOME = os.homedir();

console.log('正在检查 Python 环境...');

try {
  execSync('python3 --version', { stdio: 'pipe' });
  console.log('✓ Python 3 已安装');
} catch {
  console.error('警告: Python 3 未安装，部分功能不可用');
  console.error('请访问 https://www.python.org/downloads/ 安装');
}

try {
  execSync('python3 -c "from PIL import Image"', { stdio: 'pipe' });
  console.log('✓ Pillow 已安装');
} catch {
  try {
    console.log('正在安装 Pillow...');
    execSync('pip3 install Pillow', { stdio: 'inherit' });
    console.log('✓ Pillow 安装完成');
  } catch {
    console.error('警告: Pillow 安装失败，封面图处理功能不可用');
  }
}

// 将 Skill 软链到各模型的 skills 目录
function linkSkillTo(skillsDir, label) {
  const target = path.join(skillsDir, 'wechat-media-writer');
  try {
    fs.mkdirSync(skillsDir, { recursive: true });
    // 已存在且指向同一目录则跳过
    if (fs.existsSync(target)) {
      const cur = fs.lstatSync(target);
      if (cur.isSymbolicLink()) {
        const linkTo = fs.readlinkSync(target);
        if (path.resolve(linkTo) === path.resolve(PKG_ROOT)) {
          console.log(`✓ [${label}] Skill 已链接到最新版本`);
          return;
        }
      }
      // 指向旧版本，移除并重建
      fs.rmSync(target, { recursive: true, force: true });
    }
    fs.symlinkSync(PKG_ROOT, target, 'dir');
    console.log(`✓ [${label}] Skill 已链接: ${target} -> ${PKG_ROOT}`);
  } catch (e) {
    console.error(`警告: 无法链接 Skill 到 [${label}] ${target}: ${e.message}`);
  }
}

console.log('\n正在注册 Skill...');
linkSkillTo(path.join(HOME, '.claude', 'skills'), 'Claude Code');
linkSkillTo(path.join(HOME, '.config', 'opencode', 'skills'), 'OpenCode');

console.log('\n安装完成！');
console.log('  npx wechat-media-writer --version     # 查看版本');
console.log('  npx wechat-media-writer help           # 查看命令');
console.log('\nSkill 已自动注册，可直接说"帮我写《书名》书评发到公众号"');