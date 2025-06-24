# Dida365 To Obsidian

一个将滴答清单（Dida365）任务、项目、习惯等数据导出为 Obsidian 友好格式的 Python 工具，支持多种 Markdown 结构和日历摘要，适合个人知识管理和任务归档。

## 📋 项目简介

Dida365 To Obsidian 专为滴答清单用户设计，自动导出任务、项目、习惯等数据为 Markdown 文件，兼容 Obsidian，支持双向链接、Front Matter、日历摘要等特性。

---

## ✨ 主要功能

- **任务导出**：将所有未完成任务导出为独立 Markdown 文件，包含详细元数据、描述、子任务、父任务等。
- **项目索引**：支持统一索引（`TasksInbox.md`）和分项目索引（`Projects/项目名.md`）。
- **日历摘要**：自动生成每日、每周、每月任务摘要，结构清晰，便于回顾。
- **习惯导出**：支持滴答清单习惯打卡数据的导出与统计。
- **智能链接**：自动生成任务间父子关系、项目归属等 Obsidian 友好链接。
- **时间格式化**：所有时间均自动转换为北京时间，支持自定义格式。
- **本地安全**：所有数据仅在本地处理，账号信息安全可控。

---

## 🏗️ 目录结构

```
Dida365_To_Obsidian/
├── src/
│   ├── Dida365Client.py      # 滴答清单 API 客户端
│   ├── TaskExporter.py       # 任务导出器
│   ├── CalendarExporter.py   # 日历摘要导出器
│   ├── Types.py              # 数据模型定义
│   └── ...
├── requirements.txt
├── env.example
├── README.md
└── ...
```

---

## ⚙️ 环境配置

### 依赖安装

```bash
pip install -r requirements.txt
```

### 账号与环境变量

- 推荐使用 `.env` 文件存储账号、token 信息，避免密码暴露。
- 支持通过环境变量传递账号信息。
- token、inbox_id 首次登录后自动写入 `.env`，后续复用。

`.env` 示例：

```
DIDA365_USERNAME=your_email@example.com
DIDA365_PASSWORD=your_password
OUTPUT_DIR=/path/to/output
DIDA365_TOKEN=None
DIDA365_INBOX_ID=None
```

优先级顺序：参数传入 > 环境变量 > `.env` 文件 > 当前目录。

---

## 🧩 主要模块与用法

### 1. Dida365Client

滴答清单 API 客户端，负责登录、token 管理、数据获取。

**主要参数：**

- `username`、`password`：账号信息，可省略（自动读取环境变量或 .env）

**主要方法：**

- `get_all_data()`：获取所有项目、任务、标签等数据
- `get_projects()`：获取项目列表
- `get_project_tasks(project_id, to_date, limit)`：获取指定项目的任务
- `get_task(task_id)`：获取单个任务详情
- `get_completed_tasks(from_date, to_date, limit)`：获取已完成任务
- `get_abandoned_tasks(status, limit)`：获取已放弃任务
- `get_task_comments(project_id, task_id)`：获取任务评论
- `get_trash_tasks()`：获取回收站任务
- `get_habits()`：获取习惯列表
- `get_habits_checkins(after_stamp, habitIds)`：获取习惯打卡记录

**自动 token 管理：**

- 首次登录自动保存 token 到 .env，后续优先复用本地 token。

### 2. TaskExporter

任务导出器，将滴答清单任务数据导出为 Markdown 文件。

**主要参数：**

- `client`：Dida365Client 实例
- `output_dir`：输出目录（可选）
- `unified_index`：是否生成统一索引（默认 True）

**主要方法：**

- `export_project_tasks(project_id='')`：导出所有/指定项目的未完成任务
- `_create_task_markdown(task, task_dict)`：生成单个任务 Markdown 文件
- `_create_project_index(project, tasks, project_dir)`：生成项目索引文件
- `_get_project_index_content(project, tasks)`：返回项目索引内容字符串

**输出结构：**

- `Tasks/`：所有任务 Markdown 文件
- `Projects/`：分项目索引模式下的项目索引
- `TasksInbox.md`：统一索引模式下的总索引

**任务文件内容：**

- Front Matter（元数据）
- 任务描述
- 子任务/父任务表格
- 任务列表（如有）

### 3. CalendarExporter

日历摘要导出器，自动生成每日、每周、每月任务摘要。

**主要参数：**

- `client`：Dida365Client 实例
- `output_dir`：输出目录（可选）

**主要方法：**

- `export_daily_summary(date=None)`：导出指定/当天的每日摘要
- `export_weekly_summary(date=None)`：导出指定/当前周的周摘要
- `export_monthly_summary(date=None)`：导出指定/月的月摘要

**摘要内容：**

- 每日：分待办、已完成、习惯打卡
- 每周：按天分组，展示每日待办/已完成
- 每月：按周分组，展示每周待办/已完成

**输出结构：**

- `Calendar/Daily/`：每日摘要
- `Calendar/Weekly/`：每周摘要
- `Calendar/Monthly/`：每月摘要

### 4. Types

数据模型定义，包含 Task、Project、Tag、Habit 四个主要类。

- **Task**：任务所有属性（id、title、projectId、priority、dueDate、content、childIds、parentId、status、createdTime、modifiedTime、completedTime 等）
- **Project**：项目属性（id、name、color、sortOrder、modifiedTime 等）
- **Tag**：标签属性（name、color、sortOrder 等）
- **Habit**：习惯属性（id、name、color、status、reminders、repeatRule、createdTime、totalCheckIns 等）

---

## 📁 输出文件结构

```
output_directory/
├── Tasks/                    # 任务文件目录
│   ├── task_id_1.md          # 任务文件
│   ├── task_id_2.md
│   └── ...
├── Projects/                 # 项目文件目录（分项目索引模式）
│   ├── 项目名称1.md           # 项目索引文件
│   ├── 项目名称2.md
│   └── ...
├── TasksInbox.md             # 统一索引模式下的项目索引
└── Calendar/
    ├── Daily/
    ├── Weekly/
    └── Monthly/
```

### 任务文件格式

- Front Matter：任务元数据（title、task_id、project_id、start_date、due_date、priority、status、created_time、modified_time）
- 任务描述
- 任务列表（如有）
- 子任务表格（如有）
- 父任务表格（如有）

### 项目索引文件格式

- 统一索引：`TasksInbox.md`，所有项目任务按项目标题分区
- 分项目索引：每个项目一个 md 文件，内容包含项目元数据和任务列表

### 日历摘要格式

- 日报：分待办任务（数字列表）、已完成任务（带完成时间）、习惯打卡
- 周报：以日期为节点，每天分待办/已完成
- 月报：以周为节点，每周分待办/已完成

---

## 🔒 数据安全与隐私

- 所有数据仅在本地处理，不上传第三方服务器。
- 推荐使用 `.env` 文件存储账号和 token 信息，避免密码暴露。
- `.env` 文件应加入 `.gitignore`，避免泄露。
- 请妥善保管账号信息。

---

## 📝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：[devqiaoyu@aliyun.com]

---

**注意**：本项目仅供学习和个人使用，请遵守滴答清单的服务条款。
