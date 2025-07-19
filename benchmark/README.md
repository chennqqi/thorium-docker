# Thorium Docker Performance Benchmark

性能基准测试工具，用于对比 [chromedp/docker-headless-shell](https://github.com/chromedp/docker-headless-shell) 和 Thorium Docker 容器的性能差异。

## 功能特性

- **多容器对比**: 对比 chromedp/headless-shell 和 Thorium 不同指令集版本
- **全面测试**: 启动时间、页面加载速度、内存使用等指标
- **自动化测试**: 支持多次迭代测试，生成统计报告
- **详细报告**: 生成 Markdown 格式的详细性能报告
- **资源监控**: 实时监控容器 CPU、内存使用情况

## 测试容器

| 容器 | 描述 | 端口 |
|------|------|------|
| `chromedp/headless-shell:latest` | 参考容器 | 9222 |
| `thorium-headless:avx2` | Thorium AVX2 版本 | 9223 |
| `thorium-headless:avx` | Thorium AVX 版本 | 9224 |
| `thorium-headless:sse3` | Thorium SSE3 版本 | 9225 |
| `thorium-headless:sse4` | Thorium SSE4 版本 | 9226 |

## 测试指标

### 启动性能
- 容器启动时间
- 浏览器就绪时间
- 总启动时间

### 页面加载性能
- 页面加载时间
- 总操作时间
- 页面指标数据

### 资源使用
- CPU 使用率
- 内存使用量
- 网络 I/O
- 磁盘 I/O

## 快速开始

### 1. 环境准备

```bash
# 进入 benchmark 目录
cd benchmark

# 安装依赖
make setup

# 构建所有镜像
make build-all-images
```

### 2. 运行基准测试

```bash
# 运行完整基准测试
make run

# 运行本地基准测试（需要本地镜像）
make run-local

# 快速测试（单次迭代）
make quick

# 性能对比测试（多次迭代）
make compare
```

### 3. 查看结果

```bash
# 查看最新结果
make results

# 生成摘要报告
make summary
```

## 使用方法

### 命令行参数

```bash
python3 benchmark.py [选项]

选项:
  --iterations INT    测试迭代次数 (默认: 5)
  --timeout INT       操作超时时间 (默认: 30秒)
  --urls URLS         测试URL列表
  --output FILE       结果输出文件
  --report FILE       报告输出文件
```

### 示例

```bash
# 基本测试
python3 benchmark.py

# 自定义测试
python3 benchmark.py \
  --iterations 10 \
  --timeout 60 \
  --urls https://www.google.com https://www.github.com \
  --output my_results.json \
  --report my_report.md
```

### Docker Compose 方式

```bash
# 启动所有测试容器
docker-compose -f docker-compose.benchmark.yml up -d

# 运行基准测试
docker-compose -f docker-compose.benchmark.yml run benchmark-runner

# 查看结果
ls -la results/
```

## 测试 URL

默认测试 URL 包括：

- `https://www.google.com` - 搜索引擎
- `https://www.github.com` - 代码托管平台
- `https://www.stackoverflow.com` - 技术问答网站
- `https://www.wikipedia.org` - 百科全书

## 结果格式

### JSON 结果文件

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "iterations": 5,
  "test_urls": ["https://www.google.com"],
  "results": [
    {
      "image": "chromedp/headless-shell:latest",
      "success": true,
      "startup": {
        "total_startup_time": 3.45,
        "ready_time": 2.1
      },
      "page_loads": [
        {
          "success": true,
          "load_time": 1.23,
          "total_time": 1.45
        }
      ],
      "final_stats": {
        "cpu_percent": 2.5,
        "memory_usage": "156.2MiB",
        "memory_percent": 1.2
      }
    }
  ]
}
```

### Markdown 报告

生成详细的 Markdown 格式报告，包含：

- 性能摘要表格
- 详细测试结果
- 资源使用情况
- 成功率和错误信息

## 性能分析

### 启动时间对比

启动时间包括：
1. Docker 容器启动时间
2. 浏览器进程启动时间
3. 远程调试接口就绪时间

### 页面加载性能

页面加载测试包括：
1. 创建新页面
2. 导航到目标 URL
3. 等待页面完全加载
4. 收集页面指标

### 资源使用分析

监控指标包括：
- CPU 使用率百分比
- 内存使用量和百分比
- 网络 I/O 统计
- 磁盘 I/O 统计

## 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 检查 Docker 状态
   docker ps -a
   
   # 查看容器日志
   docker logs benchmark-chromedp
   ```

2. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep 922
   
   # 停止冲突容器
   docker stop $(docker ps -q)
   ```

3. **权限问题**
   ```bash
   # 确保 Docker socket 权限
   sudo chmod 666 /var/run/docker.sock
   ```

4. **内存不足**
   ```bash
   # 增加共享内存大小
   docker run --shm-size 4G ...
   ```

### 调试模式

```bash
# 启用详细日志
export PYTHONUNBUFFERED=1
python3 benchmark.py --iterations 1
```

## 自定义测试

### 添加新的测试容器

1. 在 `docker-compose.benchmark.yml` 中添加新服务
2. 在 `benchmark.py` 的 `run_all_benchmarks` 方法中添加容器配置
3. 重新运行测试

### 自定义测试 URL

```bash
python3 benchmark.py --urls \
  https://example.com \
  https://test.com \
  https://demo.com
```

### 自定义测试指标

修改 `benchmark.py` 中的测试方法，添加自定义指标收集。

## 持续集成

### GitHub Actions 集成

```yaml
- name: Run Performance Benchmark
  run: |
    cd benchmark
    make setup
    make build-all-images
    make run-local
    make summary
```

### 自动化报告

基准测试结果可以集成到 CI/CD 流程中，自动生成性能报告并发送通知。

## 性能优化建议

### 容器优化

1. **共享内存**: 使用 `--shm-size 2G` 或更大
2. **安全配置**: 使用 `--security-opt seccomp=unconfined`
3. **权限配置**: 添加 `--cap-add SYS_ADMIN`

### 测试优化

1. **预热**: 在正式测试前运行预热测试
2. **稳定期**: 容器启动后等待稳定期
3. **多次迭代**: 运行多次测试取平均值

### 环境优化

1. **资源隔离**: 在专用环境中运行测试
2. **网络优化**: 确保网络连接稳定
3. **系统资源**: 确保足够的 CPU 和内存

## 贡献

欢迎提交 Issue 和 Pull Request 来改进基准测试工具！

## 许可证

BSD 3-Clause License 