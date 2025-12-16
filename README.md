# 用户召回 Agent API

一个基于 FastAPI 的用户召回系统，支持通过短信和企业微信触达用户，并提供 H5 落地页用于优惠券领取。

## 功能特性

- 🔐 **商户登录认证** - 支持用户名密码登录
- 📦 **订单管理** - 批量创建订单数据
- 📢 **用户召回** - 创建召回任务，支持短信和企业微信触达
- 🎫 **优惠券系统** - H5 落地页展示和领取优惠券
- 📊 **数据追踪** - 记录用户点击和领取行为

## 技术栈

- **Web框架**: FastAPI
- **数据库**: MySQL (PyMySQL)
- **模板引擎**: Jinja2
- **短信服务**: 云片网 (yunpian_python_sdk)
- **企业微信**: wechatpy
- **连接池**: DBUtils

## 项目结构

```
recall-api/
├── main.py                 # 主应用入口
├── db/                     # 数据库配置和连接
│   ├── config.py          # 数据库配置
│   └── connection.py       # 连接池管理
├── services/               # 业务服务层
│   ├── base_service.py    # 基础服务类
│   ├── merchant_service.py # 商户服务
│   ├── order_service.py   # 订单服务
│   ├── recall_service.py  # 召回服务
│   └── dao/               # 数据访问层
│       ├── base_dao.py
│       ├── merchant_dao.py
│       ├── order_dao.py
│       └── recall_dao.py
├── models/                # 数据模型
├── templates/             # HTML模板
│   ├── landing.html      # 落地页
│   └── error.html        # 错误页
├── static/               # 静态文件
│   └── static.css
├── utils/                # 工具类
│   ├── sms/             # 短信工具
│   └── qywechat/       # 企业微信工具
├── .env                  # 环境变量配置（需自行创建）
├── requirements.txt      # Python依赖
└── README.md            # 项目说明
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- MySQL 5.7+

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据库配置

创建数据库并导入 SQL 文件：

```bash
mysql -u root -p < aiops.sql
```

### 4. 环境变量配置

创建 `.env` 文件，配置以下环境变量：

```env
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=aiops
DB_PASSWORD=your_password
DB_NAME=aiops
CHARSET=UTF8MB4

# 云片短信配置（可选）
YUNPIAN_API_KEY=your_yunpian_api_key

# 企业微信配置（可选）
WECHAT_CORP_ID=your_corp_id
WECHAT_SECRET=your_secret
```

### 5. 启动服务

```bash
# 开发环境
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

服务启动后，访问：
- API 文档: http://localhost:8001/docs
- 交互式 API 文档: http://localhost:8001/redoc

## API 接口文档

### 1. 登录接口

**POST** `/login`

请求体：
```json
{
  "username": "merchant_username",
  "password": "password"
}
```

响应：
```json
{
  "status_code": "200",
  "username": "merchant_username",
  "name": "商户名称",
  "token": "登录token",
  "message": "登录成功"
}
```

### 2. 创建订单

**POST** `/orders/create`

请求体：
```json
{
  "orders": [
    {
      "merchant_id": 1,
      "user_name": "张三",
      "order_amount": 100.00,
      "order_time": "2024-01-01 12:00:00"
    }
  ]
}
```

### 3. 创建召回任务

**POST** `/recalls/create`

请求体：
```json
{
  "recall_users": [
    {
      "merchant_id": 1,
      "user_name": "张三",
      "product": "产品名称",
      "product_type": "游戏",
      "contact": "13800138000",
      "contact_type": "mobile"
    }
  ]
}
```

### 4. H5 落地页

**GET** `/landing/{token}`

访问召回链接，展示优惠券信息。

### 5. 领取优惠券

**POST** `/coupon/get`

请求体：
```json
{
  "token": "recall_token",
  "username": "张三"
}
```

响应：
```json
{
  "status_code": "200",
  "message": "优惠券领取成功！请前往游戏内商城使用。"
}
```

## 开发说明

### 数据库连接

项目使用连接池管理数据库连接，配置在 `db/connection.py` 中。

### 服务层架构

- **Service层**: 业务逻辑处理
- **DAO层**: 数据访问，使用 QueryBuilder 构建 SQL

### 召回流程

1. 创建召回任务 → `/recalls/create`
2. 系统发送短信/企业微信消息（包含落地页链接）
3. 用户点击链接 → `/landing/{token}`（自动标记点击）
4. 用户领取优惠券 → `/coupon/get`（标记领取）

## 注意事项

1. **密码安全**: 当前使用 SHA256 加密，生产环境建议使用更安全的加密方式（如 bcrypt）
2. **Token 管理**: 登录 token 目前未持久化存储，建议添加 token 存储和验证机制
3. **短信模板**: 需要在云片网后台配置短信模板 ID
4. **企业微信权限**: 使用企业微信功能需要相应的 API 权限

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
