# Dida365 To Obsidian

一个将滴答清单（Dida365）和 Memos 数据导出为 Obsidian 友好格式 Markdown 文件的 Python 工具，适合个人知识管理、任务归档和日记整理。

---

## 目录结构

```
Dida365_To_Obsidian/
├── src/
│   ├── Dida365Exporter.py      # 滴答清单主导出器（支持任务、项目、习惯、摘要）
│   ├── MemosExporter.py        # Memos 导出器（每日/每周 Markdown 摘要）
│   ├── Dida365Client.py        # 滴答清单 API 客户端
│   ├── Types.py                # 数据模型定义（Task、Project、Habit、MemosRecord等）
│   ├── main.sh                 # 一键自动化运行脚本
│   └── ...
├── requirements.txt
├── env.example
├── Dockerfile
├── docker-compose.yml
└── ...
```

---

## 环境配置

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置 `.env` 文件（参考 env.example）：
   ```
   DIDA365_USERNAME=your_email@example.com
   DIDA365_PASSWORD=your_password
   OUTPUT_DIR=output
   MEMOS_API=https://memos.example.com/api/v1/memo
   MEMOS_TOKEN=your_memos_token
   MEMOS_DIR=Memos
   ```

---

## 主要功能与用法

### 1. Dida365Exporter.py

- 一站式导出滴答清单所有项目、任务、习惯数据，并生成每日、每周、每月 Markdown 摘要。
- 输出结构：
  - `output/Tasks/`：所有任务 Markdown 文件
  - `output/Calendar/1.Daily/`：每日任务摘要
  - `output/Calendar/2.Weekly/`：每周任务摘要
  - `output/Calendar/3.Monthly/`：每月任务摘要
- 运行：
  ```bash
  python src/Dida365Exporter.py
  ```

### 2. MemosExporter.py

- 支持通过 API Token 拉取 Memos 数据，自动生成每日、每周 Markdown 摘要。
- 输出结构：
  - `output/Memos/1.Daily/`：每日 Memos 文件
  - `output/Memos/2.Weekly/`：每周 Memos 摘要
- 运行：
  ```bash
  python src/MemosExporter.py
  ```

### 3. Dida365Client.py

- 滴答清单 API 封装，支持登录、token 管理、项目/任务/习惯等数据获取。
- 仅作为内部依赖模块使用。

### 4. Types.py

- 定义所有数据模型（Task、Project、Habit、MemosRecord等），便于数据结构统一和序列化。

### 5. main.sh

- 一键自动化运行脚本，适合 Docker/服务器定时任务：
  ```bash
  sh src/main.sh
  ```
- 会依次执行 Dida365Exporter.py 和 MemosExporter.py。

---

## 输出文件结构示例

```
output/
├── Tasks/
├── Calendar/
│   ├── 1.Daily/
│   ├── 2.Weekly/
│   └── 3.Monthly/
└── Memos/
    ├── 1.Daily/
    └── 2.Weekly/
```

---

## 数据安全与隐私

- 所有数据仅在本地处理，不上传第三方服务器。
- 推荐使用 `.env` 文件存储账号和 token 信息，避免密码暴露。
- `.env` 文件应加入 `.gitignore`，避免泄露。

---

## 许可证

MIT License
