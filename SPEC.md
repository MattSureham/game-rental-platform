# 游戏账号租赁平台 - 技术规格说明书

## 1. 项目概述

### 1.1 项目名称
**GameLease** - 游戏账号租赁交易平台

### 1.2 项目类型
微信小程序 (WeChat Mini Program) - C2C交易市场

### 1.3 核心功能
撮合游戏账号出租方(Lender)与租赁方(Renter)，提供押金担保交易、自动分账、交易后48小时验号机制及隐私保护通讯。

### 1.4 目标用户
- **Renter（租客）**：想要短期体验高端账号或特定游戏皮肤的玩家
- **Lender（出租者）**：闲置账号持有者，希望通过出租账号变现
- **Admin（管理员）**：平台运营方，负责仲裁纠纷和提现管理

---

## 2. 技术架构

### 2.1 技术栈

#### 后端 (API服务)
- **语言**：Python 3.9+
- **框架**：FastAPI
- **数据库**：SQLite (开发环境) / MySQL (生产环境)
- **ORM**：SQLAlchemy + Pydantic
- **认证**：JWT Token
- **任务调度**：APScheduler (用于48小时自动确认)

#### 前端 (小程序端)
- **框架**：UniApp (Vue.js 语法)
- **编译目标**：mp-weixin (微信小程序)
- **UI组件**：uView UI (适合uniapp的UI框架)
- **状态管理**：Vuex/Pinia

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      微信小程序客户端                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  首页   │  │ 发布    │  │ 订单    │  │ 我的    │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       └────────────┴────────────┴─────────────┘              │
│                         │                                    │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTPS (JSON)
┌─────────────────────────┼───────────────────────────────────┐
│                    Python FastAPI 后端                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   API Routes                         │    │
│  │  /auth/*  /products/*  /orders/*  /wallet/*        │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Business Logic Layer                   │    │
│  │  - 用户认证    - 商品管理    - 订单流程              │    │
│  │  - 资金托管    - 佣金计算    - 48小时验号           │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   Data Layer                         │    │
│  │              SQLAlchemy ORM + SQLite                │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 数据库设计

### 3.1 核心实体

#### 3.1.1 User (用户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键自增 |
| openid | String(128) | 微信openid (唯一) |
| nickname | String(64) | 昵称 |
| avatar_url | String(256) | 头像URL |
| phone | String(20) | 手机号 (可选) |
| wechat_id | String(64) | 微信号 (加密存储) |
| balance | Decimal(10,2) | 钱包余额 |
| frozen_balance | Decimal(10,2) | 冻结金额 (押金) |
| credit_score | Integer | 信誉分 (默认100) |
| role | String(16) | 角色: renter/lender/admin |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 3.1.2 Product (商品/账号表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键自增 |
| owner_id | Integer | 所有者ID (外键) |
| game_category | String(32) | 游戏分类 |
| game_name | String(64) | 游戏名称 |
| title | String(128) | 商品标题 |
| description | Text | 详细描述 |
| images | JSON | 图片URL列表 |
| hourly_price | Decimal(8,2) | 时租金 |
| daily_price | Decimal(8,2) | 日租金 (可选) |
| deposit | Decimal(10,2) | 押金金额 |
| status | String(16) | 状态: available/rented/offline |
| view_count | Integer | 浏览次数 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 3.1.3 Order (订单表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键自增 |
| order_no | String(32) | 订单号 (唯一) |
| renter_id | Integer | 租客ID (外键) |
| lender_id | Integer | 出租者ID (外键) |
| product_id | Integer | 商品ID (外键) |
| rental_type | String(16) | 租赁类型: hourly/daily |
| rental_hours | Integer | 租赁小时数 |
| rent_amount | Decimal(10,2) | 租金金额 |
| deposit_amount | Decimal(10,2) | 押金金额 |
| commission_rate | Decimal(5,2) | 佣金比例 |
| commission_fee | Decimal(10,2) | 佣金金额 |
| total_amount | Decimal(10,2) | 总金额 (租金+押金) |
| status | String(32) | 订单状态 (见下文) |
| start_time | DateTime | 开始时间 |
| end_time | DateTime | 结束时间 |
| return_time | DateTime | 归还时间 |
| verify_deadline | DateTime | 验号截止时间 |
| lender_confirm_time | DateTime | 出租者确认时间 |
| account_info | Text | 账号信息 (加密) |
| remark | Text | 备注 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 3.1.4 OrderStatus (订单状态枚举)
```
PENDING_PAYMENT    # 待支付
PAID              # 已支付/租用中
RETURNED          # 已归还/待验号
COMPLETED         # 已完成/已结算
CANCELLED         # 已取消
DISPUTE           # 纠纷中
REFUNDING         # 退款中
```

#### 3.1.5 WalletLog (资金流水表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键自增 |
| user_id | Integer | 用户ID (外键) |
| order_id | Integer | 订单ID (外键, 可选) |
| amount | Decimal(10,2) | 金额 |
| type | String(32) | 流水类型 |
| direction | String(8) | 方向: income/expense |
| balance_before | Decimal(10,2) | 变动前余额 |
| balance_after | Decimal(10,2) | 变动后余额 |
| description | String(256) | 描述 |
| created_at | DateTime | 创建时间 |

#### 3.1.6 WalletLogType (资金流水类型枚举)
```
RECHARGE         # 充值
PAYMENT          # 支付租金
DEPOSIT_PAY      # 支付押金
DEPOSIT_REFUND   # 押金退还
RENTAL_INCOME    # 租金收入
COMMISSION       # 佣金支出
WITHDRAWAL       # 提现
```

---

## 4. 核心业务流程

### 4.1 交易流程图

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  发布账号  │───▶│  选购账号 │───▶│  支付    │───▶│  租用中  │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                    │
                    ┌──────────┐    ┌──────────┐    │
                    │  返还押金  │◀───│  验号确认  │◀───┘
                    │  租金到账  │    │  (48小时) │
                    └──────────┘    └──────────┘
```

### 4.2 详细流程说明

#### 步骤1: 账号发布 (Lender)
1. Lender 填写账号信息 (游戏类型、描述、截图)
2. 设置租金价格 (时租/日租)
3. 设置押金金额
4. 填写微信号 (系统加密存储)
5. 提交审核 (可选) 或直接上架

#### 步骤2: 选购 (Renter)
1. Renter 浏览商品列表
2. 查看商品详情 (无法看到卖家微信号)
3. 选择租赁时长
4. 点击立即租用

#### 步骤3: 支付 (资金托管)
1. Renter 确认订单
   - 总金额 = 租金 + 押金
2. 调用微信支付 (模拟/沙箱)
3. 支付成功后:
   - 资金进入平台托管账户
   - 订单状态变为 PAID
   - **解锁卖家微信号** (仅此时可见)

#### 步骤4: 账号交付
1. Renter 在订单详情页查看卖家微信号
2. Renter 复制微信号，添加卖家微信
3. 卖家通过微信发送账号密码或扫码登录
4. 租赁计时开始

#### 步骤5: 归还
1. Renter 使用完毕后，点击"确认归还"
2. 或等待租赁时间自动结束
3. 订单状态变为 RETURNED
4. 系统开启48小时验号倒计时

#### 步骤6: 验号确认 (核心)
- **情况A (正常)**:
  1. Lender 点击"确认无误"
  2. 或48小时倒计时结束无操作
  3. 系统自动结算:
     - 扣除佣金: `租金 × 10%`
     - 剩余租金打入 Lender 钱包
     - 全额押金退还 Renter
  4. 订单状态变为 COMPLETED

- **情况B (异常)**:
  1. Lender 在48小时内点击"有异常"
  2. 提交异常证据
  3. 订单状态变为 DISPUTE
  4. 资金冻结，进入人工仲裁

### 4.3 佣金计算公式

```
订单金额 = 租金 + 押金
佣金 = 租金 × 10%
出租者收益 = 租金 - 佣金
押金 = 全额退还 (不参与抽成)
```

### 4.4 48小时自动确认机制

1. Renter 点击"确认归还"时
2. 系统设置 `verify_deadline = now() + 48小时`
3. 启动定时任务检查
4. 条件触发:
   - `now() >= verify_deadline` AND `status == RETURNED`
5. 自动执行结算逻辑

---

## 5. API接口设计

### 5.1 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 微信登录 |
| POST | /api/auth/register | 用户注册 |
| GET | /api/auth/profile | 获取用户信息 |
| PUT | /api/auth/profile | 更新用户信息 |
| PUT | /api/auth/wechat-id | 设置/修改微信号 |

### 5.2 商品接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/products | 商品列表 (支持筛选) |
| GET | /api/products/{id} | 商品详情 |
| POST | /api/products | 发布商品 |
| PUT | /api/products/{id} | 编辑商品 |
| DELETE | /api/products/{id} | 删除/下架商品 |
| GET | /api/products/categories | 游戏分类列表 |

### 5.3 订单接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/orders | 创建订单 |
| GET | /api/orders | 订单列表 |
| GET | /api/orders/{id} | 订单详情 |
| POST | /api/orders/{id}/pay | 支付订单 |
| POST | /api/orders/{id}/return | 确认归还 |
| POST | /api/orders/{id}/confirm | Lender确认验号 |
| POST | /api/orders/{id}/dispute | 发起维权 |
| GET | /api/orders/{id}/contact | 获取联系方式 (需权限) |

### 5.4 钱包接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/wallet/balance | 获取余额 |
| GET | /api/wallet/logs | 资金流水 |
| POST | /api/wallet/recharge | 充值 (模拟) |
| POST | /api/wallet/withdraw | 提现 |

---

## 6. 前端页面设计

### 6.1 页面结构

```
pages/
├── index/
│   └── index.vue          # 首页 (商品列表)
├── product/
│   ├── detail.vue         # 商品详情
│   └── publish.vue        # 发布商品
├── order/
│   ├── list.vue           # 订单列表
│   ├── detail.vue         # 订单详情
│   └── create.vue         # 创建订单
├── user/
│   ├── profile.vue        # 个人资料
│   ├── wallet.vue         # 钱包
│   └── settings.vue       # 设置
└── chat/
    └── index.vue          # 微信联系方式页面
```

### 6.2 底部导航栏

| 名称 | 图标 | 路径 |
|------|------|------|
| 首页 | home | /pages/index/index |
| 发布 | plus-circle | /pages/product/publish |
| 订单 | file-text | /pages/order/list |
| 我的 | user | /pages/user/profile |

### 6.3 核心页面设计

#### 首页 (商品列表)
- 顶部: 搜索栏 + 分类筛选
- 主体: 商品卡片瀑布流
- 每个卡片显示: 游戏封面、标题、时租价、押金、信誉分

#### 商品详情
- 轮播图展示
- 价格信息 (时租价、押金)
- 立即租用按钮
- **隐私保护**: 支付前微信号显示为 "支付后可见"

#### 订单详情
- 交易状态进度条
- 对方联系方式 (仅支付后可见)
- 操作按钮 (根据状态显示)

---

## 7. 安全与隐私

### 7.1 微信联系方式保护
- **支付前**: 商品详情页不显示卖家微信号
- **支付后**: 仅订单双方可见对方微信号
- **数据库**: 微信号加密存储 (AES)

### 7.2 资金安全
- 押金通过微信支付冻结
- 租金进入平台托管账户
- 结算后资金自动解冻

### 7.3 权限控制
- JWT Token 认证
- 订单参与者才能查看联系方式
- 管理员可查看所有数据

---

## 8. 验收标准

### 8.1 功能验收
- [ ] 用户可以通过微信登录
- [ ] Lender 可以发布游戏账号商品
- [ ] Renter 可以浏览和搜索商品
- [ ] Renter 可以创建和支付订单
- [ ] 支付后 Renter 可以看到卖家微信号
- [ ] Renter 可以确认归还
- [ ] Lender 可以在48小时内确认或发起维权
- [ ] 自动确认机制正常工作
- [ ] 佣金计算正确

### 8.2 性能验收
- [ ] 商品列表加载 < 1秒
- [ ] 订单状态更新无延迟

### 8.3 安全验收
- [ ] 未支付无法查看联系方式
- [ ] 非交易双方无法查看订单详情
- [ ] 微信号加密存储

---

## 9. 项目结构

```
game-rental-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置文件
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── wallet.py
│   │   ├── schemas/             # Pydantic 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   └── wallet.py
│   │   ├── routers/             # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   └── wallet.py
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── order_service.py
│   │   │   └── wallet_service.py
│   │   └── utils/               # 工具函数
│   │       ├── __init__.py
│   │       ├── security.py      # 加密解密
│   │       └── wechat.py        # 微信相关
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── pages/
│   │   ├── index/
│   │   ├── product/
│   │   ├── order/
│   │   ├── user/
│   │   └── chat/
│   ├── components/
│   ├── static/
│   ├── App.vue
│   ├── main.js
│   ├── manifest.json
│   ├── pages.json
│   └── uni.scss
│
└── README.md
```
