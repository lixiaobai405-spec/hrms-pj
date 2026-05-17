# ============================================
# HRMS 前端 Dockerfile（Vue3 + Vite）
# 多阶段构建：build（Node 18）→ runtime（Nginx）
# 构建上下文：项目根目录（docker-compose context: .）
# ============================================

# ---------- 阶段 1：构建前端 ----------
FROM node:18-alpine AS build

WORKDIR /app

# 复制依赖描述文件
COPY frontend/package.json frontend/package-lock.json ./

# 安装依赖（使用 npmmirror 国内镜像加速）
RUN npm ci --registry=https://registry.npmmirror.com

# 复制前端源代码
COPY frontend/ .

# 生产构建
RUN npm run build

# ---------- 阶段 2：Nginx 运行 ----------
FROM nginx:stable-alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
