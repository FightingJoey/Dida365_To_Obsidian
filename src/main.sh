#!/bin/sh
# 加载容器启动时的所有环境变量
export $(cat /proc/1/environ | tr '\0' '\n' | xargs)
# 执行 Dida365 导出脚本
/usr/local/bin/python3 /app/src/Dida365Exporter.py

# 执行 Memos 导出脚本
/usr/local/bin/python3 /app/src/MemosExporter.py