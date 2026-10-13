# =====================================================================
# Heritouch 后端 Docker 镜像
# 构建：docker build -t heritouch-api ./server
# 运行：docker run -p 8000:8000 --env-file server/.env heritouch-api
# =====================================================================
FROM python:3.11-slim

# 工作目录
WORKDIR /app

# 环境变量：禁止生成 pyc、输出不缓冲（便于 docker logs 查看）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 先安装依赖（利用 Docker 层缓存，源码变动不必重装依赖）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制全部源码
COPY . .

# 创建静态资源与 SQLite/Chroma 数据目录（不存在也不影响启动）
RUN mkdir -p /app/static/images/questions /app/static/audio

# 暴露端口
EXPOSE 8000

# 启动命令：uvicorn 托管 FastAPI 应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
