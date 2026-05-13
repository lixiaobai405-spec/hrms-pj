# HRMS Docker 一键部署（前后端+数据库）设计稿

## 目标

把当前 **Vue3(Vite) 前端 + FastAPI 后端 + MySQL** 变成“开箱即用”的一键部署方式：  
在目标机器安装 Docker Desktop / Docker Engine 后，执行一次命令即可启动整套系统。

非目标（本次不做）：
- 不做 K8s 部署、灰度发布、CI/CD。
- 不强制改动现有本地开发方式（仍可 `npm run dev` + `uvicorn --reload`）。

## 现状约束（从代码读取）

- 后端：`backend/main.py` 为 FastAPI，直接通过 SQLAlchemy + `text()` 查询 MySQL 表。
- 后端数据库连接：`backend/db.py` 读取 `.env` 中 `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`。
- 前端：Vite dev 通过 `vite.config.js` 把 `/api` 代理到 `http://127.0.0.1:8000`；axios 默认 `baseURL=/api`。

## 推荐方案（生产式一键部署）

使用 **docker-compose** 编排三个服务：

1. **db**：MySQL 8
   - 数据持久化：named volume（例如 `hrms_mysql_data`）
   - 自动初始化：挂载 `docker/mysql/initdb.d/*.sql` 到容器的 `/docker-entrypoint-initdb.d/`  
     说明：该目录下 SQL **仅在数据卷首次创建时执行**（后续重启不会重复导入）。

2. **api**：FastAPI（Uvicorn）
   - 镜像由 `backend/Dockerfile` 构建（Python 3.10 slim）
   - 通过环境变量指向 `db` 服务：`DB_HOST=db`、`DB_PORT=3306` 等
   - 对外仅在 compose 网络内部暴露 `8000`（不必须映射到宿主机）

3. **web**：Nginx（前端静态 + 反向代理）
   - 镜像由 `frontend/Dockerfile` 多阶段构建
     - build 阶段：Node 18 构建 `dist/`
     - runtime 阶段：Nginx 提供静态资源
   - Nginx 规则：
     - `/` → 前端静态资源
     - `/api/*` → 反代到 `api:8000`，并把 `/api` 前缀去掉（与 Vite dev 行为保持一致）
   - 对外只暴露一个入口端口：`80`（或可改为 `8080`）

### 为什么不做“单容器前后端一起跑”

单容器需要进程管理（supervisord 等），调试/扩缩容/日志分离都更麻烦；而 compose 多服务是更符合生产实践的“最小复杂度”方案。

## 配置与文件结构（拟新增/调整）

> 具体文件内容将在实现阶段落地。

- `docker-compose.yml`（根目录）
  - services: `db`, `api`, `web`
  - volumes: `hrms_mysql_data`
  - networks: 默认网络即可
- `backend/Dockerfile`
- `backend/requirements.txt`（补齐后端依赖：fastapi/uvicorn/sqlalchemy/pymysql/python-dotenv 等）
- `frontend/Dockerfile`
- `docker/nginx/default.conf`（或 `docker/nginx/nginx.conf`）
- `docker/mysql/initdb.d/01_schema.sql`（根据当前后端接口生成最小可跑 schema）
- `.env.example`（给 compose 使用的示例环境变量；真实 `.env` 不入库）
- `README.md` 或 `docs/docker.md`（一键启动/停止/重建/重置数据库说明）

## 环境变量设计

以 `.env`（docker compose 自动读取）作为统一入口，包含：

- MySQL 初始化：
  - `MYSQL_DATABASE=hrms`
  - `MYSQL_USER=hrms_user`
  - `MYSQL_PASSWORD=...`
  - `MYSQL_ROOT_PASSWORD=...`
- 后端连接：
  - `DB_HOST=db`
  - `DB_PORT=3306`
  - `DB_NAME=${MYSQL_DATABASE}`
  - `DB_USER=${MYSQL_USER}`
  - `DB_PASSWORD=${MYSQL_PASSWORD}`

## 端口与访问方式

- 访问入口：`http://localhost/`（web 容器）
- API：`http://localhost/api/...`（由 Nginx 反代到后端）
- 可选：是否映射 `3306` 到宿主机（便于本地 Navicat/Workbench 连接）

## 初始化 SQL 生成范围（最小可跑）

根据后端代码实际使用的表与字段，生成最小表结构：

- `department(dept_id, dept_name, parent_dept_id, is_deleted)`
- ``position(pos_id, pos_name, level_no, is_deleted)``
- `employee(emp_id, emp_no, emp_name, gender, phone, email, dept_id, pos_id, hire_date, status, is_deleted)`
- `salary_record(salary_id, emp_id, salary_month, base_salary, bonus, allowance, deduction, net_salary)`
- `attendance_record(att_id, emp_id, att_date, check_in, check_out, att_status, remark)`

并提供少量 seed（部门/岗位/员工）以便前端页面能直接看到数据。

## 验收标准

1. `docker compose up -d --build` 一次命令可启动三服务。
2. 浏览器打开 `http://localhost/` 能访问前端。
3. `http://localhost/api/health` 返回 `{"ok": true, ...}` 且能连通数据库。
4. 前端页面调用 `/api/*` 正常工作（由 Nginx 反代）。
5. 数据持久化：容器重启后数据不丢；提供清空重置数据库的说明命令。

