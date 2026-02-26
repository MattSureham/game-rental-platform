# GameLease - 游戏账号租赁平台

一个基于 Python (FastAPI) + UniApp (Vue.js) 开发的微信小程序游戏账号租赁平台。

## 功能特性

- **用户认证**: 微信登录、用户信息管理
- **商品市场**: 游戏账号展示、分类筛选、搜索
- **租赁交易**: 订单创建、支付、状态管理
- **押金机制**: 租金+押金托管、48小时验号期
- **佣金结算**: 10%平台佣金、自动/手动结算
- **隐私保护**: 支付后解锁联系方式、加密存储
- **资金管理**: 余额充值、提现、流水记录

## 技术架构

### 后端
- **框架**: FastAPI
- **数据库**: SQLite (开发) / MySQL (生产)
- **ORM**: SQLAlchemy
- **认证**: JWT
- **任务调度**: APScheduler

### 前端
- **框架**: UniApp (Vue.js)
- **状态管理**: Pinia
- **编译目标**: 微信小程序 (mp-weixin)

## 项目结构

```
game-rental-platform/
├── backend/                 # Python 后端
│   ├── app/
│   │   ├── main.py         # FastAPI 应用入口
│   │   ├── config.py       # 配置文件
│   │   ├── database.py    # 数据库连接
│   │   ├── models/        # SQLAlchemy 模型
│   │   ├── schemas/       # Pydantic 模型
│   │   ├── routers/       # API 路由
│   │   └── utils/         # 工具函数
│   └── requirements.txt
│
├── frontend/              # UniApp 前端
│   ├── pages/             # 页面组件
│   ├── store/             # Pinia 状态管理
│   ├── utils/             # 工具函数
│   ├── App.vue
│   ├── main.js
│   └── pages.json
│
└── SPEC.md                # 技术规格说明书
```

## 快速开始

### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境 (可选)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m app.main
```

后端服务将在 `http://localhost:8000` 启动。

### 2. 配置前端

编辑 `frontend/utils/api.js`，修改 `BASE_URL` 指向后端地址：

```javascript
const BASE_URL = 'http://localhost:8000/api'
```

### 3. 运行 UniApp 开发服务

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 运行微信小程序开发服务
npm run dev:mp-weixin
```

### 4. 在微信开发者工具中预览

1. 下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 使用 HBuilderX 或命令行编译 UniApp 项目
3. 在微信开发者工具中导入编译产物

## 核心交易流程

```
1. 发布账号 (Lender)
   ↓
2. 选购账号 (Renter)
   ↓
3. 支付 (租金 + 押金)
   ↓
4. 获取联系方式 (支付后解锁)
   ↓
5. 租赁使用
   ↓
6. 确认归还 (Renter)
   ↓
7. 48小时验号期 (Lender)
   ↓
8. 确认/维权
   ↓
9. 结算 (佣金扣除 + 押金退还)
```

## API 接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/api/auth/*` | 登录、注册、用户信息 |
| 商品 | `/api/products/*` | 商品列表、详情、发布 |
| 订单 | `/api/orders/*` | 订单管理、支付、结算 |
| 钱包 | `/api/wallet/*` | 余额、充值、提现、流水 |

## 配置说明

### 后端配置 (backend/app/config.py)

```python
# 数据库
DATABASE_URL = "sqlite:///./game_rental.db"

# JWT
SECRET_KEY = "your-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7天

# 佣金
COMMISSION_RATE = 0.10  # 10%

# 验号期限
VERIFY_DEADLINE_HOURS = 48
```

### 微信小程序配置

在 `frontend/manifest.json` 中配置微信小程序 AppID：

```json
{
  "mp-weixin": {
    "appid": "your-wechat-appid"
  }
}
```

## 注意事项

1. **微信支付**: 实际生产环境需要申请微信支付商户号
2. **域名配置**: 需要在微信小程序后台配置业务域名
3. **HTTPS**: 生产环境必须使用 HTTPS
4. **安全**: 生产环境请修改 SECRET_KEY 等敏感配置

## 许可证

MIT License
