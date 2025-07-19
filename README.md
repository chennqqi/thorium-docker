# Thorium Docker

高性能 Thorium 浏览器的 Docker 镜像，专为无头浏览器和网页抓取优化。支持多种 CPU 指令集版本。

## 项目概述

[Thorium](https://github.com/Alex313031/thorium) 是基于 Chromium 90 二次开发的性能优化版浏览器，相比 Chromium 原版性能提升 8%-38%。本项目提供自动化的 Docker 镜像构建和发布，支持：

- 🚀 自动检测 Thorium 新版本
- 🔄 GitHub Actions 自动化构建
- 🐳 Docker Hub 自动发布
- 🌍 多语言支持（CJK 字体）
- 🔒 安全加固配置
- 📸 截图和网页抓取优化
- ⚡ **多指令集支持**（AVX2, AVX, SSE3, SSE4）
- 📊 **性能基准测试**（对比 chromedp/docker-headless-shell）

## 指令集支持

| 指令集 | 性能 | 兼容性 | 推荐使用场景 |
|--------|------|--------|-------------|
| **AVX2** | 最高 | 现代 CPU (2013+) | 生产环境，高性能需求 |
| **AVX** | 高 | 较老 CPU (2011+) | 平衡性能和兼容性 |
| **SSE3** | 中等 | 老 CPU (2004+) | 基础兼容性需求 |
| **SSE4** | 基础 | 最广泛 | 最大兼容性 |

## 特性

- **性能优化**: 基于 Thorium 的高性能浏览器引擎
- **无头模式**: 专为自动化测试和网页抓取设计
- **多语言支持**: 内置 CJK 字体和字符集支持
- **安全加固**: 非 root 用户运行，安全配置
- **远程调试**: 支持 Chrome DevTools 远程调试
- **自动化**: 完整的 CI/CD 流水线
- **多指令集**: 支持 AVX2, AVX, SSE3, SSE4 四种版本
- **性能基准**: 完整的性能测试和对比报告

## 快速开始

### 使用 Docker Compose

```bash
# 启动 AVX2 版本（推荐）
docker-compose up -d thorium-headless-avx2

# 启动 AVX 版本
docker-compose up -d thorium-headless-avx

# 启动 SSE3 版本
docker-compose up -d thorium-headless-sse3

# 启动 SSE4 版本
docker-compose up -d thorium-headless-sse4

# 访问远程调试接口
curl http://localhost:9222/json/version  # AVX2
curl http://localhost:9223/json/version  # AVX
curl http://localhost:9224/json/version  # SSE3
curl http://localhost:9225/json/version  # SSE4
```

### 使用 Docker 命令

```bash
# 拉取 AVX2 版本（推荐）
docker pull sort/thorium-headless:latest

# 拉取特定指令集版本
docker pull sort/thorium-headless:AVX2
docker pull sort/thorium-headless:AVX
docker pull sort/thorium-headless:SSE3
docker pull sort/thorium-headless:SSE4

# 运行 AVX2 容器
docker run -d \
  --name thorium-headless-avx2 \
  -p 9222:9222 \
  --security-opt seccomp=unconfined \
  --cap-add SYS_ADMIN \
  sort/thorium-headless:AVX2

# 运行 AVX 容器
docker run -d \
  --name thorium-headless-avx \
  -p 9223:9222 \
  --security-opt seccomp=unconfined \
  --cap-add SYS_ADMIN \
  sort/thorium-headless:AVX
```

### 使用 Selenium

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 配置连接到远程浏览器
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")  # AVX2
# chrome_options.add_experimental_option("debuggerAddress", "localhost:9223")  # AVX

# 连接到浏览器
driver = webdriver.Chrome(options=chrome_options)

# 执行操作
driver.get("https://example.com")
screenshot = driver.save_screenshot("screenshot.png")
```

## 开发

### 本地构建

```bash
# 安装依赖
make install

# 构建 AVX2 版本（默认）
make build

# 构建所有指令集版本
make build-all

# 构建特定指令集版本
make build-avx2
make build-avx
make build-sse3
make build-sse4

# 运行测试
make test

# 启动本地开发环境
make run-avx2  # 启动 AVX2 版本
make run-avx   # 启动 AVX 版本
```

### 版本管理

```bash
# 检查最新版本
make version-check

# 构建特定版本和指令集
make build-version VERSION=M130.0.6723.174 INSTRUCTION_SET=AVX2

# 查看指令集信息
make info
```

## 性能基准测试

### 运行基准测试

```bash
# 运行完整基准测试
make benchmark

# 运行快速基准测试
make benchmark-quick

# 运行详细对比测试
make benchmark-compare

# 查看基准测试结果
make benchmark-results

# 生成基准测试摘要
make benchmark-summary
```

### 基准测试内容

基准测试对比以下容器：

| 容器 | 描述 | 端口 |
|------|------|------|
| `chromedp/headless-shell:latest` | 参考容器 | 9222 |
| `thorium-headless:avx2` | Thorium AVX2 版本 | 9223 |
| `thorium-headless:avx` | Thorium AVX 版本 | 9224 |
| `thorium-headless:sse3` | Thorium SSE3 版本 | 9225 |
| `thorium-headless:sse4` | Thorium SSE4 版本 | 9226 |

### 测试指标

- **启动时间**: 容器启动到浏览器就绪的总时间
- **页面加载时间**: 页面完全加载的时间
- **内存使用**: 容器运行时的内存占用
- **CPU 使用率**: 容器运行时的 CPU 使用情况
- **成功率**: 测试操作的成功率

### GitHub Actions 自动化

项目配置了自动化的性能基准测试：

- **定时测试**: 每周日自动运行基准测试
- **PR 测试**: 提交 PR 时自动运行基准测试
- **手动触发**: 可手动触发基准测试
- **自动报告**: 生成详细的性能对比报告

## 配置

### 环境变量

- `THORIUM_VERSION`: Thorium 版本号
- `INSTRUCTION_SET`: 指令集版本 (AVX2, AVX, SSE3, SSE4)
- `DISPLAY`: X11 显示设置
- `LANG`: 语言环境设置

### 浏览器参数

默认启动参数已针对无头模式优化：

```bash
thorium \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --disable-dev-shm-usage \
  --remote-debugging-port=9222 \
  --disable-web-security \
  --disable-features=VizDisplayCompositor
```

## 自动化

### GitHub Actions

项目配置了完整的自动化流水线：

1. **版本检测**: 每日检查 Thorium 新版本
2. **自动构建**: 发现新版本时自动构建所有指令集版本
3. **自动发布**: 推送到 Docker Hub
4. **自动标签**: 根据版本号和指令集创建标签
5. **性能基准**: 自动运行性能测试和对比

### 手动触发

在 GitHub 仓库页面可以手动触发构建：

1. 进入 Actions 页面
2. 选择 "Build and Push Docker Image" 或 "Performance Benchmark"
3. 点击 "Run workflow"
4. 可选择指定版本号和指令集

### 镜像标签

每个版本都会生成以下标签：

- `latest-avx2`, `avx2` - AVX2 版本
- `latest-avx`, `avx` - AVX 版本  
- `latest-sse3`, `sse3` - SSE3 版本
- `latest-sse4`, `sse4` - SSE4 版本
- `{version}-avx2` - 特定版本的 AVX2 构建
- `{version}-avx` - 特定版本的 AVX 构建
- `{version}-sse3` - 特定版本的 SSE3 构建
- `{version}-sse4` - 特定版本的 SSE4 构建

## 选择指令集

### 如何选择

1. **AVX2** (推荐): 现代服务器和桌面环境
2. **AVX**: 较老的服务器或需要平衡性能和兼容性
3. **SSE3**: 老旧的硬件或虚拟机环境
4. **SSE4**: 最大兼容性，适用于各种环境

### 检测 CPU 指令集

```bash
# Linux
grep -o 'avx2\|avx\|sse3\|sse4' /proc/cpuinfo | head -1

# macOS
sysctl -n machdep.cpu.features | grep -o 'AVX2\|AVX\|SSE3\|SSE4'

# Windows (PowerShell)
Get-WmiObject -Class Win32_Processor | Select-Object -ExpandProperty Architecture
```

## 安全考虑

- 使用非 root 用户运行
- 禁用不必要的功能
- 安全沙箱配置
- 最小化攻击面

## 性能优化

- 禁用 GPU 加速（容器环境）
- 优化内存使用
- 禁用后台进程
- 精简依赖包
- 指令集优化

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 检查日志
   docker logs thorium-headless-avx2
   
   # 检查端口占用
   netstat -tulpn | grep 9222
   ```

2. **指令集不兼容**
   ```bash
   # 检查 CPU 指令集
   grep -o 'avx2\|avx\|sse3\|sse4' /proc/cpuinfo
   
   # 尝试使用兼容性更好的版本
   docker run sort/thorium-headless:sse4
   ```

3. **远程调试连接失败**
   ```bash
   # 检查容器状态
   docker ps
   
   # 检查网络连接
   curl http://localhost:9222/json/version
   ```

4. **字体显示问题**
   ```bash
   # 检查字体安装
   docker exec thorium-headless-avx2 fc-list
   ```

5. **基准测试失败**
   ```bash
   # 检查基准测试环境
   cd benchmark
   make setup
   make benchmark-quick
   ```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

BSD 3-Clause License

## 参考

- [Thorium Browser](https://github.com/Alex313031/thorium)
- [ChromeDP Docker Headless Shell](https://github.com/chromedp/docker-headless-shell)
- [Chrome Headless](https://developers.google.com/web/updates/2017/04/headless-chrome)
- [CPU Instruction Sets](https://en.wikipedia.org/wiki/Advanced_Vector_Extensions)
