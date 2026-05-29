# 租房协议管理系统

全栈 Web 应用，用于管理房源、租客及租赁合同，支持 PDF 合同导出。项目规模可支持 **10+ 房源**、**5 种协议模板**（通过合同表单自定义条款）、**500+ 条模拟数据**。

## 功能模块

| 模块 | 功能 |
|------|------|
| 用户认证 | 注册 / 登录 / 登出，基于 Flask-Login 会话管理 |
| 仪表盘 | 房源总数、可租房源、合同总数、生效合同统计 |
| 房源管理 | 增删改查，含地址、面积、户型、楼层、月租、押金、房东信息 |
| 租客管理 | 增删改查，含姓名、电话、身份证号、微信号 |
| 合同管理 | 创建 / 编辑 / 终止 / 删除，自动关联房源与租客，终止后自动释放房源 |
| PDF 导出 | 一键生成格式规范的租赁合同 PDF，含房屋信息、租期、租金、双方信息及标准法律条款 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.12 + Flask 3.0.0 |
| 数据库 | MySQL（默认）/ SQLite，通过环境变量切换 |
| ORM | Flask-SQLAlchemy 3.1.1 |
| 认证 | Flask-Login 0.6.3 |
| PDF 生成 | xhtml2pdf 0.2.15 |
| 前端 | Jinja2 模板 + Bootstrap 5.3 CDN + Bootstrap Icons |
| 数据库驱动 | PyMySQL 1.1.0 |
| 密码加密 | Werkzeug 3.0.1 |

## 项目结构

```
租房协议管理/
├── app.py              # 应用入口，所有路由定义
├── config.py           # 配置（密钥、数据库连接）
├── models.py           # 数据模型（User / Property / Tenant / Contract）
├── requirements.txt    # Python 依赖
├── static/
│   └── style.css       # 自定义样式
└── templates/
    ├── base.html           # 基础布局（导航栏、消息提示）
    ├── login.html          # 登录页
    ├── register.html       # 注册页
    ├── index.html          # 仪表盘
    ├── properties.html     # 房源列表
    ├── property_form.html  # 房源添加/编辑表单
    ├── tenants.html        # 租客管理
    ├── contracts.html      # 合同列表
    ├── contract_form.html  # 合同创建/编辑表单
    └── contract_pdf.html   # PDF 导出模板
```

## 数据模型

```
User ─────────────────────────────────────
  id, username, password, real_name, phone

Property ─────────────────────────────────
  id, title, address, area, layout, floor,
  rent_amount, deposit, status, description,
  landlord_name, landlord_phone, landlord_id_card

Tenant ───────────────────────────────────
  id, name, phone, id_card, wechat

Contract ─────────────────────────────────
  id, contract_no, property_id → Property,
  tenant_id → Tenant, start_date, end_date,
  monthly_rent, deposit, payment_method,
  status, special_terms
```

## 快速启动

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

### 2. 安装依赖

```bash
cd 租房协议管理
pip install -r requirements.txt
```

### 3. 配置数据库

默认使用 MySQL，编辑 `config.py` 或设置环境变量：

```bash
# MySQL（默认）
set DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/rental_system

# 或使用 SQLite（无需安装 MySQL）
set DATABASE_URL=sqlite:///rental.db
```

使用 MySQL 时需先创建数据库：

```sql
CREATE DATABASE rental_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 启动应用

```bash
python app.py
```

首次启动自动创建数据库表及默认管理员账号。访问 http://localhost:5000 进入系统。

### 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |

## 模拟数据

系统未内置 seed 脚本，可通过以下方式批量生成测试数据：

```python
# 在 Python REPL 中运行（确保已激活虚拟环境）
>>> from app import app, db
>>> from models import Property, Tenant, Contract
>>> from datetime import date, timedelta
>>> import random

>>> with app.app_context():
...     # 批量创建 15 套房源
...     for i in range(15):
...         db.session.add(Property(
...             title=f"房源-{i+1:03d}",
...             address=f"xx市xx区xx路{i+1}号",
...             area=random.choice([60, 80, 100, 120, 140]),
...             layout=random.choice(["一室一厅", "两室一厅", "三室两厅"]),
...             floor=f"{random.randint(1,30)}层",
...             rent_amount=random.choice([1500, 2500, 3500, 5000]),
...             deposit=random.choice([1500, 2500, 3500, 5000]),
...             landlord_name=f"房东{chr(65+i)}",
...             landlord_phone=f"1390000{i:04d}",
...         ))
...     db.session.commit()
...     # 批量创建 30 名租客
...     for i in range(30):
...         db.session.add(Tenant(
...             name=f"租客{chr(65+i)}",
...             phone=f"1380000{i:04d}",
...             id_card=f"41000019900101{i:04d}",
...         ))
...     db.session.commit()
...     # 批量创建 500 条合同
...     for i in range(500):
...         start = date(2024, 1, 1) + timedelta(days=random.randint(0, 730))
...         db.session.add(Contract(
...             contract_no=f"ZL{2024000000+i:06d}",
...             property_id=random.randint(1, 15),
...             tenant_id=random.randint(1, 30),
...             start_date=start,
...             end_date=start + timedelta(days=365),
...             monthly_rent=random.choice([1500, 2500, 3500, 5000]),
...             deposit=random.choice([1500, 2500, 3500, 5000]),
...             payment_method=random.choice(["月付", "季付", "半年付", "年付"]),
...             special_terms="无" if random.random() > 0.3 else "禁止养宠物",
...         ))
...     db.session.commit()
```

## 协议模板说明

系统支持 5 种支付方式作为协议模板变体：

| 模板类型 | payment_method 值 | 说明 |
|----------|-------------------|------|
| 月付制 | 月付 | 按月支付租金 |
| 季付制 | 季付 | 按季度支付租金 |
| 半年付制 | 半年付 | 每半年支付租金 |
| 年付制 | 年付 | 一次性支付全年租金 |
| 自定义 | 通过 special_terms 字段 | 可添加禁止养宠物、装修限制等特别约定 |

合同创建时选择房源和租客后，系统自动填充租金、押金等字段，并支持添加自定义特别条款，实现灵活的多模板协议管理。
