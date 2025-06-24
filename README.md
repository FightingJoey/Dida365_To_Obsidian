# Dida365 To Obsidian

一个将滴答清单（Dida365）任务数据导出为 Obsidian 友好格式的 Python 工具。

## 📋 项目简介

Dida365 To Obsidian 是一个专门用于将滴答清单中的任务和项目数据导出为 Markdown 格式的工具，生成的文档完全兼容 Obsidian 笔记软件，支持双向链接、Front Matter 等 Obsidian 特性。

## ✨ 主要功能

### 🔄 数据导出

- **任务导出**：将滴答清单中的未完成任务导出为独立的 Markdown 文件
- **项目索引**：支持两种模式：
  - 默认：只生成一个 `TasksInbox.md`，所有项目任务索引合并在一起，按项目标题分区
  - 可选：为每个项目单独生成索引文件，保存在 `Projects/` 目录
- **智能链接**：自动生成任务间的父子关系链接，支持 `[[id|title]]` 格式
- **时间格式化**：自动将时间转换为北京时间，支持多种时间格式

### 📊 数据结构

- **任务详情**：包含标题、描述、优先级、截止时间、创建时间、完成时间等完整信息
- **任务关系**：支持父子任务关系，自动生成关联链接
- **项目组织**：按项目分类组织任务，生成项目索引文件或统一索引
- **优先级显示**：使用特殊符号标记显示任务优先级（⏬、🔽、🔼、⏫）

### 🗓️ 日历摘要

- 自动创建 `Calendar/Daily`、`Calendar/Weekly`、`Calendar/Monthly` 目录
- **每日摘要**：分"待办任务"（有序数字列表）和"已完成任务"（带完成时间）
- **每周摘要**：以日期为节点，每天分"待办任务"和"已完成任务"
- **每月摘要**：以周为节点，每周分"待办任务"和"已完成任务"

### 🎯 Obsidian 集成

- **Front Matter**：每个任务文件包含完整的元数据
- **双向链接**：支持 Obsidian 的双向链接功能
- **表格展示**：使用 Markdown 表格展示子任务、父任务
- **文件夹结构**：自动创建 `Tasks/`、`Projects/`、`Calendar/` 等文件夹

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 滴答清单账号

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

1. **克隆项目**

```bash
git clone <repository-url>
cd Dida365_To_Obsidian
```

2. **配置账号信息**

**方法 1：使用 .env 文件（推荐）**

复制环境变量示例文件：

```bash
cp env.example .env
```

编辑 `.env` 文件，填入你的账号信息：

```bash
# 你的滴答清单用户名/邮箱
DIDA365_USERNAME=your_email@example.com

# 你的滴答清单密码
DIDA365_PASSWORD=your_password

# 输出目录（可选，默认为当前脚本所在目录）
OUTPUT_DIR=/path/to/output/directory

# token（首次运行自动写入）
DIDA365_TOKEN=None
DIDA365_INBOX_ID=None
```

**方法 2：使用环境变量**

在终端中设置环境变量：

```bash
# Linux/macOS
export DIDA365_USERNAME="your_email@example.com"
export DIDA365_PASSWORD="your_password"
export OUTPUT_DIR="/path/to/output/directory"  # 可选
```

3. **运行导出**

```bash
python TaskExporter.py
```

### 高级使用

#### 导出指定项目

```python
from TaskExporter import TaskExporter
from Dida365Client import Dida365Client

client = Dida365Client()
# 只导出指定项目
exporter = TaskExporter(client)
exporter.export_project_tasks(project_id="your_project_id")
# 导出所有项目
exporter.export_project_tasks()
```

#### 统一索引与分项目索引

```python
# 统一索引（默认）：只生成一个 TasksInbox.md
exporter = TaskExporter(client, unified_index=True)
# 分项目索引：每个项目生成独立索引文件
exporter = TaskExporter(client, unified_index=False)
```

#### 日历摘要导出

```python
from CalendarExporter import CalendarExporter
exporter = CalendarExporter(client)
exporter.export_daily_summary()
exporter.export_weekly_summary()
exporter.export_monthly_summary()
```

## 📁 输出结构

```
output_directory/
├── Tasks/                    # 任务文件目录
│   ├── task_id_1.md         # 任务文件
│   ├── task_id_2.md
│   └── ...
├── Projects/                # 项目文件目录（分项目索引模式）
│   ├── 项目名称1.md         # 项目索引文件
│   ├── 项目名称2.md
│   └── ...
├── TasksInbox.md            # 统一索引模式下的项目索引
└── Calendar/
    ├── Daily/
    ├── Weekly/
    └── Monthly/
```

### 任务文件格式

每个任务文件包含：

- **Front Matter**：任务的元数据信息（包括 title、task_id、project_id、start_date、due_date、priority、status、created_time、modified_time）
- **任务描述**：任务的详细内容
- **任务列表**：任务的子项列表（如果有）
- **子任务列表**：以表格形式展示子任务（如果有）
- **父任务信息**：以表格形式展示父任务（如果有）

### 项目索引文件格式

- **统一索引**：`TasksInbox.md`，所有项目任务按项目标题分区
- **分项目索引**：每个项目一个 md 文件，内容包含项目元数据和任务列表

### 日历摘要格式

- **日报**：分"待办任务"（数字列表）和"已完成任务"（带完成时间）
- **周报**：以日期为节点，每天分"待办任务"和"已完成任务"
- **月报**：以周为节点，每周分"待办任务"和"已完成任务"

## 🔧 API 文档

### Dida365Client

滴答清单 API 客户端，提供数据获取功能。

#### 主要方法

- `get_all_data()`: 获取所有数据（项目、任务、标签）
- `get_projects()`: 获取项目列表
- `get_task(task_id)`: 获取指定任务信息
- `get_completed_tasks(from_date, to_date, limit=50)`: 获取已完成任务
- `get_habits()`: 获取习惯列表

### TaskExporter

任务导出器，负责将数据转换为 Markdown 格式。

#### 主要方法

- `export_project_tasks(project_id='')`: 导出项目任务（支持统一索引和分项目索引）
- `_create_task_markdown(task, task_dict)`: 创建单个任务文件
- `_create_project_index(project, tasks, project_dir)`: 创建项目索引文件

### CalendarExporter

日历摘要导出器，负责导出每日、每周、每月任务摘要。

#### 主要方法

- `export_daily_summary(date=None)`: 导出每日摘要
- `export_weekly_summary(date=None)`: 导出每周摘要
- `export_monthly_summary(date=None)`: 导出每月摘要

### Types

数据模型定义，包含 Task、Project、Tag 三个主要类。

#### Task 类

包含任务的所有属性：

- `id`: 任务唯一标识
- `title`: 任务标题
- `projectId`: 所属项目 ID
- `priority`: 优先级（1-5）
- `dueDate`: 截止时间
- `content`: 任务描述
- `childIds`: 子任务 ID 列表
- `parentId`: 父任务 ID
- `status`: 任务状态
- `createdTime`: 创建时间
- `modifiedTime`: 修改时间
- `completedTime`: 完成时间

#### Project 类

包含项目的主要属性：

- `id`: 项目唯一标识
- `name`: 项目名称
- `color`: 项目颜色
- `sortOrder`: 项目排序
- `modifiedTime`: 修改时间

#### Tag 类

包含标签的主要属性：

- `name`: 标签名称
- `color`: 标签颜色
- `sortOrder`: 标签排序

## 🔒 安全说明

- **.env 文件优先**：推荐使用 `.env` 文件存储账号和 token 信息，避免密码暴露在代码中
- **本地处理**：所有数据仅在本地处理，不会上传到第三方服务器
- **.env 文件安全**：确保 `.env` 文件已添加到 `.gitignore` 中，不会被提交到版本控制
- **账号安全**：请妥善保管你的滴答清单账号信息，不要分享给他人

## 📝 配置选项

### 输出目录配置

输出目录的优先级顺序：

1. **参数传入**：`TaskExporter(client, "/path/to/output")`
2. **环境变量**：`OUTPUT_DIR="/path/to/output"`（可在 `.env` 文件中设置）
3. **当前目录**：使用脚本文件所在目录

```python
# 示例1：通过参数指定
exporter = TaskExporter(client, "/Users/username/Documents/obsidian")

# 示例2：通过 .env 文件或环境变量指定
# 在 .env 文件中设置：OUTPUT_DIR="/Users/username/Documents/obsidian"
exporter = TaskExporter(client)

# 示例3：使用当前目录（默认）
exporter = TaskExporter(client)
```

### 时间格式

支持自定义时间格式：

```python
# 默认格式：YYYY-MM-DD HH:MM:SS
formatted_time = self._format_time(time_str)

# 自定义格式：YYYY-MM-DD
formatted_time = self._format_time(time_str, "%Y-%m-%d")
```

### 优先级显示

优先级标记规则：

- 低优先级：🔽
- 中优先级：🔼
- 高优先级：⏫
- 无优先级：⏬

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢滴答清单提供的 API 服务
- 感谢 Obsidian 团队开发的优秀笔记软件
- 感谢所有贡献者的支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：[devqiaoyu@aliyun.com]

---

**注意**：本项目仅供学习和个人使用，请遵守滴答清单的服务条款。
