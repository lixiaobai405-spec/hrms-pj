# HRMS 人力资源管理系统（Vue3 + FastAPI + MySQL Docker）

## 1. 项目结构
```
hrms-pj/
├── backend/           # FastAPI 后端
├── frontend/          # Vue3 前端
├── docker/
│   ├── mysql/
│   │   └── initdb.d/  # 数据库初始化 SQL（自动执行）
│   └── nginx/
│       └── default.conf  # Nginx 反代配置
├── docs/              # 报告、截图、ER图等
├── .env.example       # 环境变量模板
└── docker-compose.yml # 一键部署编排
```

## 2. 运行环境
- Node.js 18+
- Python 3.10（conda 环境：hrms）
- Docker Desktop

---

## 3. 一键部署（Docker Compose，推荐）

**首次启动：**
```powershell
# 1. 复制环境变量模板
copy .env.example .env

# 2. 一键构建并启动
docker compose up -d --build
```

**三个服务自动启动：**

| 服务 | 容器名 | 说明 |
|---|---|---|
| MySQL 8 | hrms-mysql | 自动建表 + 导入示例数据 |
| FastAPI | hrms-api | 后端 API，内部端口 8000 |
| Nginx+前端 | hrms-web | 唯一对外入口，端口 80 |

**访问：**
- 前端页面：http://localhost
- Swagger 文档：http://localhost/api/docs
- 健康检查：http://localhost/health

**常用命令：**
```powershell
# 停止
docker compose down

# 重启
docker compose up -d

# 完全重置（清空数据库，重新初始化）
docker compose down -v
docker compose up -d --build

# 查看日志
docker compose logs -f api
```

---

## 4. 本地开发（不使用 Docker）

### 4.1 启动数据库（MySQL Docker）
```powershell
docker ps
docker start hr-mysql
```

### 4.2 启动后端（FastAPI）
Anaconda Prompt：
```bat
conda activate hrms
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

验证：
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

### 4.3 启动前端（Vue3）
```bat
cd frontend
npm install
npm run dev
```

打开：http://localhost:5173

---

## 5. 前后端联调方式（/api）
- 开发环境：Vite proxy 转发 `/api` → `http://127.0.0.1:8000`
- Docker 部署：Nginx 反代 `/api/` → `http://api:8000/`

## 6. 常见问题
- **Docker 部署后页面空白**：确认 `docker compose logs web` 和 `docker compose logs api`
- **/health 500**：确认 MySQL 容器已启动且健康检查通过
- **前端本地开发跨域**：本项目使用 Vite proxy（/api）规避跨域
- **端口冲突**：宿主机 80 端口被占用时，修改 `docker-compose.yml` 中 `ports: "8080:80"`
