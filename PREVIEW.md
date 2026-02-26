# 小程序预览指南

## 预览方式

### 方式一：HBuilderX (推荐，最简单)

HBuilderX 是 uni-app 官方推荐的 IDE，内置了编译器和模拟器。

#### 步骤 1：下载 HBuilderX
访问: https://www.dcloud.io/hbuilderx.html

下载 **正式版** (建议使用 Windows 版本)

#### 步骤 2：导入项目
1. 打开 HBuilderX
2. 文件 → 导入 → 从本地项目导入
3. 选择 `D:\minimax\game-rental-platform\frontend` 文件夹
4. 点击确定

#### 步骤 3：运行预览
1. 在 HBuilderX 左侧项目管理器中，右键点击 `frontend` 项目
2. 选择 **运行** → **运行到浏览器** (可先在浏览器查看)
3. 或选择 **运行** → **运行到小程序模拟器** → **微信开发者工具**

---

### 方式二：命令行 + 微信开发者工具

#### 步骤 1：安装依赖

```bash
# 1. 安装 Node.js
# 访问 https://nodejs.org/ 下载并安装 LTS 版本

# 2. 进入前端目录
cd D:\minimax\game-rental-platform\frontend

# 3. 安装依赖
npm install
```

#### 步骤 2：启动后端 API

```bash
# 新开一个命令行窗口

# 进入后端目录
cd D:\minimax\game-rental-platform\backend

# 创建虚拟环境 (可选)
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python -m app.main
```

后端启动后，API 地址: `http://localhost:8000`

#### 步骤 3：修改 API 地址

编辑 `frontend/utils/api.js`:
```javascript
// 开发环境使用本地地址
const BASE_URL = 'http://localhost:8000/api'
```

#### 步骤 4：编译 UniApp

```bash
cd D:\minimax\game-rental-platform\frontend

# 开发模式编译 (热更新)
npm run dev:mp-weixin
```

编译产物在: `unpackage\dist\dev\mp-weixin`

#### 步骤 5：用微信开发者工具预览

1. 下载微信开发者工具: https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
2. 打开微信开发者工具
3. 点击 **导入项目**
4. 选择编译产物目录: `D:\minimax\game-rental-platform\frontend\unpackage\dist\dev\mp-weixin`
5. 点击预览

---

## 目录结构说明

```
frontend/
├── unpackage/           # 编译产物目录
│   └── dist/
│       └── dev/
│           └── mp-weixin/  # 微信小程序编译产物
│
├── pages/               # 页面源代码
│   ├── index/          # 首页
│   ├── product/       # 商品页
│   ├── order/         # 订单页
│   ├── user/          # 用户页
│   └── chat/          # 聊天页
│
├── utils/
│   └── api.js         # API 接口配置
│
└── pages.json         # 页面路由配置
```

---

## 常见问题

### Q1: 微信开发者工具打不开?
A: 需要在微信公众平台注册小程序账号，获取 AppID，并在开发者工具中登录

### Q2: 后端连接失败?
A: 
1. 确保后端服务已启动 (`python -m app.main`)
2. 检查端口 8000 是否被占用
3. 防火墙是否允许

### Q3: 页面空白?
A: 
1. 清除缓存后重新编译
2. 检查微信开发者工具的详情 → 本地设置 → 关闭 "es6 转 es5"

### Q4: 如何查看后端日志?
A: 后端运行的控制台会显示请求日志，包括：
- 请求路径
- 响应状态
- 错误信息

---

## 快速检查清单

| 项目 | 状态 |
|------|------|
| Node.js 已安装 | ☐ |
| npm install 已执行 | ☐ |
| 后端服务已启动 (端口 8000) | ☐ |
| API 地址已配置 | ☐ |
| 微信开发者工具已安装 | ☐ |
| 微信开发者工具已登录 | ☐ |

---

## 下一步

预览成功后，你可以：

1. **体验完整流程**
   - 注册/登录
   - 发布商品
   - 创建订单
   - 测试支付流程

2. **配置生产环境**
   - 购买云服务器
   - 部署后端
   - 申请微信支付

3. **提交审核发布**
   - 上传代码
   - 提交审核
   - 发布上线
