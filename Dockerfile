# 基于官方最小化 Python 镜像，支持多架构（armv7, arm64, amd64）
FROM --platform=$BUILDPLATFORM python:3.11-slim AS base

# 设置工作目录
WORKDIR /app

# 先复制 requirements.txt
COPY requirements.txt /app/requirements.txt

# 安装 cron 和必要依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制代码
COPY src/ /app/src/

RUN chmod +x /app/src/login.sh
RUN chmod +x /app/src/task.sh
RUN chmod +x /app/src/calendar.sh

# 创建输出目录（可被宿主机挂载）
RUN mkdir -p /output

# 拷贝示例 .env 文件
COPY env.example /app/.env

# 设置环境变量（可由 docker run -e 传入）
ENV PYTHONUNBUFFERED=1 \
    OUTPUT_DIR=/output

# 默认定时任务：每小时执行一次导出脚本
# 用户可通过挂载自定义 crontab 文件覆盖 /etc/cron.d/dida_cron
COPY docker_crontab /etc/cron.d/dida_cron
RUN chmod 0644 /etc/cron.d/dida_cron && crontab /etc/cron.d/dida_cron

# 启动 cron 服务
# 可通过挂载 /output 实现数据持久化
CMD ["cron", "-f"]

# =====================
# 使用说明（中文）：
# 1. 构建镜像（支持多架构）：
#    docker buildx build --platform linux/arm/v7,linux/arm64,linux/amd64 -t dida365-obsidian:latest .
# 2. 运行容器并挂载输出目录：
#    docker run -d -e DIDA365_USERNAME=xxx -e DIDA365_PASSWORD=xxx -v /your/output:/output dida365-obsidian:latest
# 3. 如需自定义定时任务，可挂载自定义 crontab 文件覆盖 /etc/cron.d/dida_cron
# 4. 也可进入容器手动执行：
#    docker exec -it <container_id> python /app/src/TaskExporter.py
#    docker exec -it <container_id> python /app/src/CalendarExporter.py
# ===================== 