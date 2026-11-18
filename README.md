# 观微元 DeltaScope

观微元是一个面向数学学习的微信小程序，包含学习内容、每周一题、作答批改、论坛、知识图谱和学习数据等功能。

本项目由三部分组成：

- `backend/`：Python Flask API 服务
- `frontend/miniprogram/`：微信小程序前端
- `database/schema.sql`：MySQL 建表和示例数据脚本

## 推荐方式：Docker 本地启动

这是最适合第一次部署的方式。Docker 会自动准备 Python 运行环境、项目依赖和 MySQL，电脑上不需要另外安装 Python 或 MySQL。

### 需要安装什么

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。安装后启动 Docker Desktop，确认它处于运行状态。
2. 安装最新版[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)。
3. 获取本项目代码，并在终端进入项目根目录，也就是能看到 `docker-compose.yml` 的目录。

### 1. 启动后端和数据库

在项目根目录执行：

```bash
docker compose up -d --build
```

第一次启动会下载镜像、构建后端并初始化数据库，可能需要几分钟。查看运行状态：

```bash
docker compose ps
```

后端启动后，用浏览器打开下面两个地址：

- [http://127.0.0.1:5051/health/live](http://127.0.0.1:5051/health/live)：返回 `{"status":"ok"}` 表示服务已启动
- [http://127.0.0.1:5051/health/ready](http://127.0.0.1:5051/health/ready)：返回 `{"status":"ok"}` 表示数据库连接正常

查看后端日志：

```bash
docker compose logs -f backend
```

按 `Ctrl+C` 只会退出日志查看，不会停止服务。停止服务：

```bash
docker compose down
```

数据库和上传文件保存在 Docker volume 中，执行 `down` 不会删除它们。需要重新初始化一个空数据库时才执行：

```bash
docker compose down -v
docker compose up -d --build
```

`down -v` 会删除本地数据库数据，请确认不再需要旧数据后再执行。

### 2. 在微信开发者工具中打开小程序

1. 打开微信开发者工具，选择“导入项目”。
2. 项目目录选择本项目中的 `frontend/miniprogram`，不要选择仓库根目录。
3. AppID 可以使用项目配置中的测试 AppID，也可以改成自己的小程序 AppID。
4. 打开“详情 -> 本地设置”，确认“**不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书**”已勾选。它只适用于本地联调，正式发布前必须关闭并配置 HTTPS 合法域名。
5. 点击编译。前端默认请求 `http://127.0.0.1:5051`，与上面的 Docker 端口一致，不需要改代码。

### 3. 第一次登录

- 学生：在小程序中注册一个 11 位手机号，密码至少 8 位。
- 教师：先注册学生账号，在“我的”页面使用教师认证码 `gdutmath` 认证。这个值来自 `docker-compose.yml`，只用于本地演示，部署到其他环境时应修改。
- 管理员：本地 Compose 默认账号是 `admin`，密码是 `admin12345`。这是开发默认值，正式环境必须修改。

如果只想验证后端，不需要先登录，直接访问两个健康检查地址即可。

### Docker 常见问题

**端口 5051 被占用**：修改 `docker-compose.yml` 中的端口映射，例如改为 `5052:5051`，同时把 `frontend/miniprogram/config/index.js` 中的 `BASE_URL` 改成 `http://127.0.0.1:5052`，然后重新执行 `docker compose up -d --build`。

**`health/ready` 返回 unavailable**：执行 `docker compose logs db backend`。通常是数据库仍在第一次初始化，等待几十秒后再刷新；也可能是旧 volume 中的数据与当前配置不一致。

**小程序提示网络错误**：确认后端容器正在运行，并在开发者工具中关闭合法域名校验。真机调试时，`127.0.0.1` 指向手机本身，需要改成电脑在局域网中的 IP，并让后端监听 `0.0.0.0`。

**修改了 `schema.sql` 但数据库没有变化**：MySQL 只会在空 volume 第一次创建时执行初始化脚本。确认数据可以删除后，执行 `docker compose down -v` 再启动。

## 不使用 Docker 的本地安装方式

如果电脑不能使用 Docker，也可以手动安装 Python 3.9+、MySQL 8.0+ 和微信开发者工具。

### 1. 初始化 MySQL

先用 MySQL 管理员账号登录：

```bash
mysql -u root -p
```

在 MySQL 中执行下面的 SQL。请把 `change-this-password` 换成你自己的本地数据库密码：

```sql
CREATE DATABASE IF NOT EXISTS deltascope
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'deltascope'@'127.0.0.1'
  IDENTIFIED BY 'change-this-password';
GRANT ALL PRIVILEGES ON deltascope.* TO 'deltascope'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;
```

导入表结构和示例数据：

macOS/Linux：

```bash
mysql -u root -p deltascope < database/schema.sql
```

Windows PowerShell：

```powershell
Get-Content database/schema.sql | mysql -u root -p deltascope
```

### 2. 安装后端依赖

macOS/Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

复制配置模板：

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，至少填写：

```dotenv
DB_PASSWORD=change-this-password
ADMIN_PASSWORD=admin12345
TOKEN_SECRET=local-development-secret
TEACHER_AUTH_CODE=gdutmath
```

后端不会自动读取 `.env` 文件，需要在启动前把变量加载到当前终端。macOS/Linux 使用：

```bash
set -a
source backend/.env
set +a
python backend/main.py
```

Windows PowerShell 使用：

```powershell
Get-Content backend/.env | Where-Object { $_ -and $_ -notmatch '^\s*#' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$name" -Value $value
}
python backend/main.py
```

看到后端监听 `5051` 后，再按上面的微信开发者工具步骤导入 `frontend/miniprogram`。

## 运行测试

手动安装方式下，在项目根目录执行。macOS/Linux：

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tests/run_checks.py
```

Windows PowerShell：

```powershell
python -m unittest discover -s tests -v
python tests/run_checks.py
```

测试会检查配置、服务启动、接口行为以及数据库连通性，因此需要先启动 MySQL 并正确加载环境变量。

## 生产部署提醒

Docker Compose 配置用于本地开发，里面的管理员密码、教师认证码和 token 密钥都是开发默认值，不能直接用于公网环境。正式部署至少需要：

- 使用独立的 MySQL 账号，不使用 root；
- 设置 `APP_ENV=production`、随机且不少于 32 个字符的 `TOKEN_SECRET`、管理员密码、教师认证码和微信 AppID/AppSecret；
- 使用 HTTPS 反向代理，并在微信公众平台配置合法域名；
- 为数据库和上传目录配置持久化备份；
- 不把 `.env`、真实密钥和生产数据库密码提交到 Git。
