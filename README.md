# 观微元 (DeltaScope)

观微元 - 观察 · 推导 · 见证成长

## 项目结构

整个项目分为三个主要部分：

- `backend/`: Python Flask 后端 API 服务
- `frontend/miniprogram/`: 微信小程序前端代码
- `database/`: 数据库建表脚本
- `tests/`: 接口测试与验证脚本

## 环境要求

- **Python**: 3.9 或更高版本
- **MySQL**: 8.0 或更高版本
- **微信开发者工具**: 最新版

## 快速启动指南

### 1. 数据库准备

1. 创建数据库及专用应用账号。部署环境不要使用 MySQL root 账号。
2. 运行 `database/schema.sql`：
   ```sql
   CREATE DATABASE IF NOT EXISTS deltascope DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   USE deltascope;
   -- 执行 schema.sql 中的建表语句
   ```

### 2. 后端部署 (Flask)

1. 从项目根目录创建虚拟环境并安装依赖：

   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. 复制 `backend/.env.example` 为 `backend/.env`，配置数据库密码、管理员密码、教师授权码和随机 `TOKEN_SECRET`。配置文件不会自动加载，启动前导出变量：

   ```bash
   set -a
   . backend/.env
   set +a
   ```
3. 启动开发服务器：

   ```bash
   python backend/main.py
   ```

   服务地址为 `http://127.0.0.1:5051`。开发服务器只用于本地调试。

### 3. 生产启动

生产环境需设置 `APP_ENV=production` 并提供全部必需密钥；应用会在缺少配置时拒绝启动。使用 Waitress 等 WSGI 容器运行，生产入口为 `main:app`，工作目录为 `backend/`：

```bash
waitress-serve --listen=127.0.0.1:5051 main:app
```

公网部署时应由 HTTPS 反向代理转发至 WSGI 服务，上传目录需配置持久化存储，并限制其 Web 访问策略。

### 4. 前端部署 (微信小程序)

1. 打开 **微信开发者工具**。
2. 选择 **导入项目**，目录选择到 `frontend/miniprogram` 文件夹。
3. 在开发者工具中，如果提示 AppID，可填入您自己的 AppID，或点击“测试号”。
4. 本地联调时，在 **详情 -> 本地设置** 中关闭合法域名校验；线上环境必须配置 HTTPS 合法域名并重新开启校验。

## 测试与校验

项目中包含了用于测试的脚本：

- `.venv/bin/python -m unittest discover -s tests -v`：运行单元和接口测试（含数据库连通检查）。
- `.venv/bin/python tests/run_checks.py`：运行项目检查脚本。
