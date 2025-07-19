# Thorium Docker 项目需求文档

## 项目概述
thorium-docker 项目: thorium for docker
目标: 通过github action自动构建thorium镜像，并发布到docker hub

## 技术背景
- thorium是基于chromium 90二次开发的性能优化版chromium版本
- 相比chromium原版性能高8%-38%
- 参考项目: https://github.com/chromedp/docker-headless-shell
- thorium github地址: https://github.com/Alex313031/thorium
- thorium release下载地址: https://github.com/Alex313031/thorium/releases/tag/M130.0.6723.174

## 核心需求

### 1. 版本管理
- 周期性获取thorium新版本
- 按照版本打tag

### 2. 自动化构建
- 自动构建docker镜像
- 发布到docker hub

### 3. 运行环境优化
- 参考chromedp/docker-headless-shell项目
- 安装字体、语言、字符集
- 保证截图、多语言等浏览器基础功能正常使用
- 为无头浏览器抓取做优化
- 包括性能、安全性等优化

### 4. 多指令集支持 ⭐ 新增
- 支持 AVX2 版本（高性能）
- 支持 AVX 版本（中等性能）
- 支持 SSE3 版本（基础性能）
- 支持 SSE4 版本（兼容性）
- 自动检测 CPU 指令集并选择合适的版本
- 为不同指令集构建对应的 Docker 镜像标签

### 5. 性能基准测试 ⭐ 新增
- 对比 chromedp/docker-headless-shell 和本项目的性能
- 测试不同指令集版本的性能差异
- 包含启动时间、内存使用、页面加载速度等指标
- 生成详细的性能报告
- 支持自动化性能测试

## 技术要求
- 使用GitHub Actions进行CI/CD
- Docker镜像构建
- 自动化版本检测和发布
- 无头浏览器环境配置
- CPU指令集检测和版本选择
- 性能基准测试框架 