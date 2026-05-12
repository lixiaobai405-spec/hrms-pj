# HRMS 人力资源管理系统（Vue3 + FastAPI + MySQL Docker）

## 1. 项目结构
```
hrms-pj/
  backend/     # FastAPI 后端
  frontend/    # Vue3 前端
  docs/        # 报告、截图、ER图等
```

## 2. 运行环境
- Node.js 18+
- Python 3.10（conda 环境：hrms）
- Docker Desktop（MySQL 8 容器：hr-mysql）

## 3. 启动数据库（MySQL Docker）
PowerShell：
```powershell
docker ps
docker start hr-mysql
```

进入数据库（可选）：
```powershell
docker exec -it hr-mysql mysql -uhrms_user -p
```

## 4. 启动后端（FastAPI）
Anaconda Prompt：
```bat
conda activate hrms
cd C:\Users\32159\hrms-pj\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

验证：
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

## 5. 启动前端（Vue3）
新终端：
```bat
cd C:\Users\32159\hrms-pj\frontend
npm install
npm run dev
```

打开：
- http://localhost:5173

## 6. 前后端联调方式（/api）
- 前端所有请求走 `/api/...`
- 开发环境通过 Vite proxy 转发到后端 `http://127.0.0.1:8000`
- 生产环境建议用 Nginx 反向代理 `/api` 到后端

## 7. 打包（生产构建）
```bat
cd frontend
npm run build
```

产物在：
- `frontend/dist/`

## 8. 常见问题
- /health 500：先确认 `docker ps` 里 hr-mysql 是否运行；再看 backend/.env 是否正确
- 前端跨域：本项目使用 Vite proxy（/api）规避跨域

