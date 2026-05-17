# ============================================
# HRMS 后端 Dockerfile（FastAPI + Uvicorn）
# 基础镜像：Python 3.10 slim
# ============================================
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（编译 cryptography 所需）
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动 Uvicorn（生产模式，非 --reload）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
