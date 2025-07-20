# 需求分析文档

## 项目概述

本项目旨在为 Thorium 浏览器提供 Docker 容器化解决方案，支持多种 CPU 指令集优化，并提供性能基准测试功能。

## 核心需求

### 1. Docker 容器化
- **目标**: 将 Thorium 浏览器打包为 Docker 镜像
- **要求**: 
  - 支持多种 CPU 指令集 (AVX2, AVX, SSE3, SSE4)
  - 无头模式运行，适合自动化测试和网页抓取
  - 安全配置，非 root 用户运行
  - 多语言支持，包含 CJK 字体

### 2. 性能基准测试
- **目标**: 对比 Thorium 与 chromedp/docker-headless-shell 的性能
- **要求**:
  - 测量启动时间、页面加载时间、内存使用、CPU 使用
  - 支持多种测试 URL 和迭代次数
  - 生成详细的性能报告
  - 集成到 CI/CD 流程中
  - 自动创建输出目录，确保基准测试脚本的健壮性

### 3. CI/CD 自动化
- **目标**: 自动化构建、测试和发布流程
- **要求**:
  - 自动检测 Thorium 新版本
  - 构建所有指令集变体
  - 运行性能基准测试
  - 发布 Docker 镜像到注册表

## 技术实现

### Thorium 安装路径
- **主程序路径**: `/opt/chromium.org/thorium/thorium-browser`
- **系统软链接**: `/usr/bin/thorium-browser` (自动创建)
- **自定义软链接**: `/usr/bin/thorium` (Dockerfile 创建)
- **包装脚本**: `/usr/bin/wrapped-thorium` (容器优化版本)

### 启动参数配置
- **基础参数**: `--ignore-gpu-blocklist`, `--no-first-run`, `--no-sandbox`
- **安全参数**: `--password-store=basic`, `--test-type`
- **容器优化**: `--simulate-outdated-no-au`, `--user-data-dir`
- **无头模式**: `--headless`, `--disable-gpu`, `--remote-debugging-port=9222`
- **性能优化**: `--disable-dev-shm-usage`, `--disable-web-security`

### 文件命名规则
- **主要格式**: `thorium-browser_${VERSION#M}_${INSTRUCTION_SET}.deb`
- **备用格式**: `thorium_${VERSION}_amd64_${INSTRUCTION_SET}.deb`
- **版本处理**: 自动移除 M 前缀（如 M130.0.6723.174 → 130.0.6723.174）

### 容器配置
- **用户**: thorium (非 root)
- **工作目录**: `/home/thorium`
- **调试端口**: 9222
- **共享内存**: 2GB
- **安全选项**: seccomp=unconfined, SYS_ADMIN capability
- **镜像名称**: 使用 `${{ secrets.DOCKER_USERNAME }}/thorium-headless` 格式
- **标签格式**: `{username}/thorium-headless:{version}-{instruction_set}`

### 安装方式
- **使用 apt install**: 自动处理所有依赖关系
- **简化依赖管理**: 无需手动安装 libcurl4, libu2f-udev 等
- **自动依赖解析**: apt 会自动下载和安装缺失的依赖包

### 系统依赖包
- **核心依赖**: libgtk-3-0, libnss3, libnspr4, libxcomposite1, libxdamage1
- **图形依赖**: libdrm2, libgbm1, libxrandr2, libxss1, libxtst6
- **音频依赖**: libasound2, libatspi2.0-0
- **字体支持**: fonts-noto-cjk, fonts-noto-color-emoji, fonts-dejavu-core
- **自动依赖**: libcurl4, libu2f-udev, libxkbcommon0 等由 apt 自动处理

## 基准测试指标

### 性能指标
1. **启动时间**: 容器启动到服务就绪的时间
2. **页面加载时间**: 页面完全加载的时间
3. **内存使用**: 峰值和平均内存使用量
4. **CPU 使用**: 平均 CPU 使用率
5. **成功率**: 测试用例的成功率

### 测试配置
- **默认迭代次数**: 5 次
- **超时时间**: 30 秒
- **测试 URL**: 包含静态页面、动态页面、复杂应用
- **容器变体**: chromedp/headless-shell, Thorium AVX2/AVX/SSE3/SSE4

## 部署架构

### Docker 镜像
- **基础镜像**: debian:bullseye-slim
- **多阶段构建**: 基础依赖 → Thorium 安装 → 最终镜像
- **标签策略**: 
  - `latest-${INSTRUCTION_SET}`
  - `${VERSION}-${INSTRUCTION_SET}`
  - `${INSTRUCTION_SET}`

### 服务编排
- **开发环境**: docker-compose.yml
- **基准测试**: docker-compose.benchmark.yml
- **生产部署**: 支持 Kubernetes 和 Docker Swarm

## 安全考虑

### 容器安全
- 非 root 用户运行
- 最小权限原则
- 安全选项配置
- 镜像签名验证

### 网络安全
- 仅暴露必要端口
- 内部网络隔离
- 防火墙规则配置

## 监控和维护

### 健康检查
- HTTP 端点检查
- 进程状态监控
- 资源使用监控

### 日志管理
- 结构化日志输出
- 日志轮转配置
- 错误追踪和报告

## 扩展性考虑

### 水平扩展
- 无状态设计
- 负载均衡支持
- 自动扩缩容

### 垂直扩展
- 资源限制配置
- 性能调优选项
- 多实例部署

## 兼容性

### 平台支持
- Linux x86_64
- Docker 20.10+
- Kubernetes 1.20+

### 浏览器兼容性
- Chrome DevTools Protocol
- Selenium WebDriver
- Puppeteer

## 未来规划

### 功能增强
- 支持 ARM64 架构
- 添加更多指令集优化
- 集成更多基准测试工具

### 性能优化
- 镜像大小优化
- 启动时间优化
- 内存使用优化

### 运维改进
- 自动化监控
- 故障恢复机制
- 性能告警系统 