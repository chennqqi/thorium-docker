# Thorium Docker 部署指南

## 概述

本指南详细说明如何部署和使用 Thorium Docker 项目，包括本地开发、CI/CD 配置和生产环境部署。

## 环境准备

### 系统要求

- **操作系统**: Linux, macOS, Windows (WSL2)
- **Docker**: 20.10.0 或更高版本
- **Docker Compose**: 2.0.0 或更高版本
- **Python**: 3.8 或更高版本 (用于测试)
- **Git**: 最新版本

### 安装 Docker

#### Ubuntu/Debian
```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置稳定版仓库
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
```

#### macOS
```bash
# 使用 Homebrew 安装
brew install --cask docker

# 或者从官网下载 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

#### Windows
1. 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 启用 WSL2 后端
3. 重启系统

### 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 设置执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

## 本地开发环境

### 1. 克隆项目

```bash
git clone https://github.com/chennqqi/thorium-docker.git
cd thorium-docker
```

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 构建镜像

```bash
# 使用 Makefile
make build

# 或直接使用 Docker
docker build -t thorium-docker:latest .
```

### 4. 运行测试

```bash
# 启动测试环境
make test

# 或手动运行
docker-compose up -d thorium-test
python3 test/test_browser.py
docker-compose down
```

### 5. 本地运行

```bash
# 启动开发环境
make run

# 验证运行状态
curl http://localhost:9222/json/version
```

## CI/CD 配置

### GitHub Actions 设置

#### 1. 创建 Docker Hub 账户

1. 访问 [Docker Hub](https://hub.docker.com)
2. 注册账户并验证邮箱
3. 创建新的仓库 (可选)

#### 2. 配置 GitHub Secrets

在 GitHub 仓库设置中配置以下 Secrets:

1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下 secrets:

```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password_or_token
```

#### 3. 创建 Docker Hub Access Token

1. 登录 Docker Hub
2. 进入 Account Settings → Security
3. 点击 "New Access Token"
4. 设置名称和权限 (Read & Write)
5. 复制生成的 token 作为 DOCKER_PASSWORD

#### 4. 触发构建

```bash
# 推送代码触发自动构建
git add .
git commit -m "Initial commit"
git push origin main

# 或手动触发
# 在 GitHub 仓库页面 → Actions → Build and Push Docker Image → Run workflow
```

### 监控构建状态

1. 进入 GitHub 仓库 Actions 页面
2. 查看工作流执行状态
3. 检查构建日志和错误信息
4. 验证 Docker Hub 发布结果

## 生产环境部署

### 单机部署

```bash
# 拉取最新镜像
docker pull chennqqi/thorium-docker:latest

# 运行容器
docker run -d \
  --name thorium-headless \
  --restart unless-stopped \
  -p 9222:9222 \
  -v thorium_data:/config \
  --security-opt seccomp=unconfined \
  --cap-add SYS_ADMIN \
  chennqqi/thorium-docker:latest
```

### Docker Compose 部署

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  thorium:
    image: chennqqi/thorium-docker:latest
    container_name: thorium-headless
    restart: unless-stopped
    ports:
      - "9222:9222"
    volumes:
      - thorium_data:/config
    environment:
      - DISPLAY=:99
    security_opt:
      - seccomp:unconfined
    cap_add:
      - SYS_ADMIN
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9222/json/version"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  thorium_data:
    driver: local
```

```bash
# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### Kubernetes 部署

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thorium-headless
  labels:
    app: thorium-headless
spec:
  replicas: 1
  selector:
    matchLabels:
      app: thorium-headless
  template:
    metadata:
      labels:
        app: thorium-headless
    spec:
      containers:
      - name: thorium
        image: chennqqi/thorium-docker:latest
        ports:
        - containerPort: 9222
        securityContext:
          capabilities:
            add:
            - SYS_ADMIN
        volumeMounts:
        - name: thorium-config
          mountPath: /config
      volumes:
      - name: thorium-config
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: thorium-service
spec:
  selector:
    app: thorium-headless
  ports:
  - protocol: TCP
    port: 9222
    targetPort: 9222
  type: ClusterIP
```

```bash
# 部署到 Kubernetes
kubectl apply -f k8s-deployment.yaml

# 查看部署状态
kubectl get pods -l app=thorium-headless
kubectl logs -l app=thorium-headless
```

## 监控和维护

### 健康检查

```bash
# 检查容器状态
docker ps | grep thorium

# 检查远程调试接口
curl http://localhost:9222/json/version

# 查看容器日志
docker logs thorium-headless
```

### 性能监控

```bash
# 查看资源使用情况
docker stats thorium-headless

# 检查内存使用
docker exec thorium-headless ps aux | grep thorium
```

### 日志管理

```bash
# 配置日志轮转
docker run -d \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --name thorium-headless \
  chennqqi/thorium-docker:latest
```

### 备份和恢复

```bash
# 备份配置数据
docker run --rm -v thorium_data:/data -v $(pwd):/backup alpine tar czf /backup/thorium-backup.tar.gz -C /data .

# 恢复配置数据
docker run --rm -v thorium_data:/data -v $(pwd):/backup alpine tar xzf /backup/thorium-backup.tar.gz -C /data
```

## 故障排除

### 常见问题

#### 1. 容器启动失败

**症状**: 容器立即退出
```bash
# 检查日志
docker logs thorium-headless

# 检查端口占用
netstat -tulpn | grep 9222

# 检查权限
docker run --rm --security-opt seccomp=unconfined --cap-add SYS_ADMIN chennqqi/thorium-docker:latest
```

**解决方案**:
- 确保使用正确的安全选项
- 检查端口是否被占用
- 验证镜像完整性

#### 2. 远程调试连接失败

**症状**: 无法连接到 9222 端口
```bash
# 检查容器状态
docker ps -a | grep thorium

# 检查网络连接
docker exec thorium-headless netstat -tulpn

# 测试端口连通性
telnet localhost 9222
```

**解决方案**:
- 重启容器
- 检查防火墙设置
- 验证端口映射

#### 3. 性能问题

**症状**: 页面加载缓慢或内存使用过高
```bash
# 检查资源使用
docker stats thorium-headless

# 调整内存限制
docker run -d --memory=2g --memory-swap=4g chennqqi/thorium-docker:latest
```

**解决方案**:
- 增加内存限制
- 优化启动参数
- 检查系统资源

#### 4. 字体显示问题

**症状**: 中文或特殊字符显示异常
```bash
# 检查字体安装
docker exec thorium-headless fc-list

# 检查语言环境
docker exec thorium-headless locale
```

**解决方案**:
- 重新构建镜像
- 检查字体包安装
- 验证语言环境设置

## 安全考虑

### 网络安全

```bash
# 限制网络访问
docker run -d \
  --network host \
  --add-host host.docker.internal:host-gateway \
  chennqqi/thorium-docker:latest
```

### 资源限制

```bash
# 设置资源限制
docker run -d \
  --memory=2g \
  --cpus=2.0 \
  --pids-limit=100 \
  chennqqi/thorium-docker:latest
```

### 安全扫描

```bash
# 使用 Trivy 扫描镜像
trivy image chennqqi/thorium-docker:latest

# 使用 Docker Scout
docker scout cves chennqqi/thorium-docker:latest
```

## 更新和维护

### 自动更新

项目配置了自动更新机制，但也可以手动更新：

```bash
# 检查新版本
make version-check

# 手动触发构建
# 在 GitHub Actions 中手动运行工作流
```

### 版本回滚

```bash
# 回滚到特定版本
docker run -d chennqqi/thorium-docker:M130.0.6723.174

# 更新标签
docker tag chennqqi/thorium-docker:M130.0.6723.174 chennqqi/thorium-docker:latest
```

## 支持和贡献

### 获取帮助

- 查看 [README.md](README.md) 获取基本信息
- 提交 [GitHub Issue](https://github.com/chennqqi/thorium-docker/issues)
- 查看 [故障排除](#故障排除) 部分

### 贡献代码

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

### 报告问题

在提交 Issue 时，请包含以下信息：
- 操作系统和版本
- Docker 版本
- 错误日志
- 重现步骤
- 预期行为 