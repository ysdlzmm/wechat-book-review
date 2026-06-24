#!/usr/bin/env node

const { execSync } = require('child_process');

console.log('正在检查 Python 环境...');

try {
  // 检查 Python 3
  execSync('python3 --version', { stdio: 'pipe' });
  console.log('✓ Python 3 已安装');
  
  // 检查并安装 Pillow
  try {
    execSync('python3 -c "from PIL import Image"', { stdio: 'pipe' });
    console.log('✓ Pillow 已安装');
  } catch {
    console.log('正在安装 Pillow...');
    execSync('pip3 install Pillow', { stdio: 'inherit' });
    console.log('✓ Pillow 安装完成');
  }
  
  console.log('\n安装完成！使用方法:');
  console.log('  npx wechat-book-review help');
  
} catch (e) {
  console.error('\n警告: Python 3 未安装');
  console.error('请手动安装 Python 3: https://www.python.org/downloads/');
  console.error('\n安装后仍可使用，但需要手动运行 Python 脚本');
}
