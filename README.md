# 观微元 (DeltaScope)

观微元 - 观察 · 推导 · 见证成长

## 项目结构

整个项目分为三个主要部分：

- `backend/`: Python Flask 后端 API 服务
- `frontend/miniprogram/`: 微信小程序前端代码
- `database/`: 数据库建表脚本
- `tests/`: 接口测试与验证脚本

## 环境要求

- **Python**: 3.9 或更高版本（后端依赖类型提示新特性）
- **MySQL**: 8.0 或更高版本
- **微信开发者工具**: 最新版

## 快速启动指南

### 1. 数据库准备

1. 打开本地 MySQL 数据库。
2. 运行 `database/schema.sql` 脚本：
   ```sql
   CREATE DATABASE IF NOT EXISTS deltascope DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   USE deltascope;
   -- 执行 schema.sql 中的建表语句
   ```

### 2. 后端部署 (Flask)

1. 进入后端目录：

   ```bash
   cd backend
   ```
2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```
3. 配置环境变量（可选，或直接修改 `backend/app/config.py`）：

   - 修改 `config.py` 中的 `DB_CONFIG` 字典，填入本地的 MySQL 账号和密码。
4. 启动后端服务：

   ```bash
   python main.py
   ```

   后端服务默认将运行在 `http://127.0.0.1:5000`。

### 3. 前端部署 (微信小程序)

1. 打开 **微信开发者工具**。
2. 选择 **导入项目**，目录选择到 `frontend/miniprogram` 文件夹。
3. 在开发者工具中，如果提示 AppID，可填入您自己的 AppID，或点击“测试号”。
4. 在开发者工具右上角点击 **详情 -> 本地设置**，勾选 **“不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书”**。

## 测试与校验

项目中包含了用于测试的脚本：

- `python tests/test_db_connection.py`：测试数据库连接是否正常。
- `python tests/test_register_api.py`：测试注册接口连通性。
