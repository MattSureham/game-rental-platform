# GameLease 部署指南

## 项目概述

GameLease 是一个游戏账号租赁平台微信小程序，包含：
- **后端**: Python FastAPI API 服务
- **前端**: UniApp 微信小程序

---

## 一、本地开发环境部署

### 1. 后端部署

```bash
# 进入后端目录
cd D:\minimax\game-rental-platform\backend

# 创建虚拟环境 (推荐)
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m app.main
```

服务启动后访问: `http://localhost:8000`

### 2. 前端开发

```bash
# 进入前端目录
cd D:\minimax\game-rental-platform\frontend

# 安装依赖
npm install

# 安装 uni-app CLI (如果没有)
npm install -g @vue/cli

# 运行微信小程序开发模式
npm run dev:mp-weixin
```

编译产物在: `unpackage/dist/dev/mp-weixin`

---

## 二、生产环境部署

### 方案 A: 后端部署到云服务器

#### 1. 服务器准备
- 购买云服务器 (阿里云/腾讯云)
- 安装 Python 3.9+
- 安装 Nginx
- 配置域名并申请 SSL 证书

#### 2. 部署后端

```bash
# SSH 连接到服务器
ssh user@your-server-ip

# 安装 Python 和相关工具
sudo apt update
sudo apt install python3 python3-pip nginx

# 上传代码
git clone https://github.com/MattSureham/game-rental-platform.git
cd game-rental-platform/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 使用 Systemd 管理服务
sudo nano /etc/systemd/system/gamelease.service
```

**gamelease.service 内容:**
```ini
[Unit]
Description=GameLease API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/game-rental-platform/backend
ExecStart=/var/www/game-rental-platform/backend/venv/bin/python -m app.main
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl enable gamelease
sudo systemctl start gamelease

# 配置 Nginx 反向代理
sudo nano /etc/nginx/sites-available/gamelease
```

**Nginx 配置:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/gamelease /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 方案 B: 使用 Docker 部署 (推荐)

#### 1. 创建 Dockerfile

**backend/Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./game_rental.db
      - SECRET_KEY=your-secret-key
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "8080:80"
```

---

## 三、微信小程序发布

### 1. 微信小程序账号申请

1. 访问 [微信公众平台](https://mp.weixin.qq.com/)
2. 注册小程序账号
3. 完成企业认证 (需要营业执照)

### 2. 配置小程序

1. 登录微信公众平台
2. 设置 → 基本信息 → 填写小程序信息
3. 开发管理 → 开发设置:
   - 获取 AppID
   - 设置服务器域名 (request合法域名)
   - 设置业务域名

### 3. 配置后端域名

在 `frontend/utils/api.js` 中修改:
```javascript
const BASE_URL = 'https://api.yourdomain.com/api'
```

### 4. 编译小程序

```bash
# 生产环境编译
cd frontend
npm run build:mp-weixin
```

编译产物在: `dist/build/mp-weixin`

### 5. 上传审核

1. 下载微信开发者工具
2. 导入编译产物目录
3. 点击上传
4. 在公众平台提交审核
5. 审核通过后发布

---

## 四、阿里云/腾讯云部署示例

### 阿里云 ECS 部署

```bash
# 1. 购买 ECS 实例 (CentOS 8)
# 2. 安全组开放端口: 80, 443, 22

# 3. 安装 Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 4. 拉取并运行后端
docker run -d -p 8000:8000 \
  --name gamelease-api \
  -e DATABASE_URL=sqlite:///./game_rental.db \
  your-docker-image

# 5. 配置 Nginx
sudo yum install nginx
# ... (配置如上文)
```

---

## 五、关键配置说明

### 1. 微信支付配置

需要申请微信支付商户号，配置:
```python
# backend/app/config.py
WECHAT_MCHID = "your_mch_id"
WECHAT_API_KEY = "your_api_key"
WECHAT_NOTIFY_URL = "https://yourdomain.com/api/wallet/notify"
```

### 2. 数据库配置

开发环境使用 SQLite，生产环境使用 MySQL:
```python
# MySQL 配置示例
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/gamelease"
```

### 3. 安全配置

```python
# 生产环境务必修改
SECRET_KEY = "随机生成的密钥"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7天
```

---

## 六、常见问题

### Q1: 数据库文件在哪里?
A: SQLite 数据库文件在 `backend/app/game_rental.db`

### Q2: 如何查看日志?
```bash
# Docker 方式
docker logs gamelease-api

# Systemd 方式
journalctl -u gamelease -f
```

### Q3: 小程序提示"需要授权"?
A: 检查微信公众平台的 AppID 和 AppSecret 是否正确配置

### Q4: 支付功能无法使用?
A: 
1. 需要申请微信支付商户号
2. 需要完成企业认证
3. 需要配置支付授权目录

---

## 七、架构图

```
┌─────────────────────────────────────────────────────────┐
│                     微信小程序客户端                        │
│                   (用户手机)                              │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────┐
│                      云服务器                             │
│  ┌─────────────────┐    ┌─────────────────┐           │
│  │   Nginx         │───▶│  FastAPI 后端   │           │
│  │   (反向代理)     │    │  (8000端口)     │           │
│  └─────────────────┘    └────────┬────────┘           │
│                                  │                     │
│                         ┌────────▼────────┐          │
│                         │   MySQL 数据库   │          │
│                         └─────────────────┘          │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   微信支付 API      │
              └─────────────────────┘
```

---

## 联系支持

如有问题，请提交 GitHub Issue:
https://github.com/MattSureham/game-rental-platform/issues
