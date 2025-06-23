# Dida365 To Obsidian

一个将滴答清单（Dida365）任务数据导出为 Obsidian 友好格式的 Python 工具。

## 📋 项目简介

Dida365 To Obsidian 是一个专门用于将滴答清单中的任务和项目数据导出为 Markdown 格式的工具，生成的文档完全兼容 Obsidian 笔记软件，支持双向链接、Front Matter 等 Obsidian 特性。

## ✨ 主要功能

### 🔄 数据导出
- **任务导出**：将滴答清单中的未完成任务导出为独立的 Markdown 文件
- **项目索引**：为每个项目生成包含任务列表的索引文件
- **智能链接**：自动生成任务间的父子关系链接，支持 `[[id|title]]` 格式
- **时间格式化**：自动将时间转换为北京时间，支持多种时间格式

### 📊 数据结构
- **任务详情**：包含标题、描述、优先级、截止时间、创建时间等完整信息
- **任务关系**：支持父子任务关系，自动生成关联链接
- **项目组织**：按项目分类组织任务，生成项目索引文件
- **优先级显示**：使用星级标记显示任务优先级（⭐、⭐⭐、⭐⭐⭐）

### 🎯 Obsidian 集成
- **Front Matter**：每个任务文件包含完整的元数据
- **双向链接**：支持 Obsidian 的双向链接功能
- **表格展示**：使用 Markdown 表格展示任务列表
- **文件夹结构**：自动创建 `tasks/` 和 `projects/` 文件夹

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

**方法1：使用 .env 文件（推荐）**

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
```

**方法2：使用环境变量**

在终端中设置环境变量：
```bash
# Linux/macOS
export DIDA365_USERNAME="your_email@example.com"
export DIDA365_PASSWORD="your_password"
export OUTPUT_DIR="/path/to/output/directory"  # 可选

# Windows (CMD)
set DIDA365_USERNAME=your_email@example.com
set DIDA365_PASSWORD=your_password
set OUTPUT_DIR=C:\path\to\output\directory

# Windows (PowerShell)
$env:DIDA365_USERNAME="your_email@example.com"
$env:DIDA365_PASSWORD="your_password"
$env:OUTPUT_DIR="C:\path\to\output\directory"
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

# 方法1：使用 .env 文件（推荐）
client = Dida365Client()

# 方法2：直接传入参数（不推荐）
# client = Dida365Client(username="your_email", password="your_password")

# 创建导出器 - 输出目录优先级：参数 > 环境变量 > 当前目录
exporter = TaskExporter(client)  # 使用 .env 文件或环境变量或当前目录
# exporter = TaskExporter(client, "/path/to/output/directory")  # 指定输出目录

# 导出指定项目
exporter.export_project_tasks(project_id="your_project_id")

# 导出所有项目
exporter.export_project_tasks()
```

## 📁 输出结构

```
output_directory/
├── tasks/                    # 任务文件目录
│   ├── task_id_1.md         # 任务文件
│   ├── task_id_2.md
│   └── ...
└── projects/                # 项目文件目录
    ├── 项目名称1.md         # 项目索引文件
    ├── 项目名称2.md
    └── ...
```

### 任务文件格式
每个任务文件包含：
- **Front Matter**：任务的元数据信息
- **任务描述**：任务的详细内容
- **子任务列表**：以表格形式展示子任务
- **父任务链接**：指向父任务的链接

### 项目文件格式
每个项目文件包含：
- **项目信息**：项目的基本信息
- **任务列表**：以表格形式展示项目下的所有任务

## 🔧 API 文档

### Dida365Client

滴答清单 API 客户端，提供数据获取功能。

#### 主要方法
- `get_all_data()`: 获取所有数据（项目、任务、标签）
- `get_projects()`: 获取项目列表
- `get_task(task_id)`: 获取指定任务信息
- `get_completed_tasks()`: 获取已完成任务
- `get_habits()`: 获取习惯列表

### TaskExporter

任务导出器，负责将数据转换为 Markdown 格式。

#### 主要方法
- `export_project_tasks(project_id='')`: 导出项目任务
- `_create_task_markdown(task, task_dict)`: 创建单个任务文件
- `_create_project_index(project, tasks, project_dir)`: 创建项目索引文件

### Types

数据模型定义，包含 Task、Project、Tag 三个主要类。

#### Task 类
包含任务的所有属性：
- `id`: 任务唯一标识
- `title`: 任务标题
- `projectId`: 所属项目ID
- `priority`: 优先级（1-5）
- `dueDate`: 截止时间
- `content`: 任务描述
- `childIds`: 子任务ID列表
- `parentId`: 父任务ID

## 🔒 安全说明

- **.env 文件优先**：推荐使用 `.env` 文件存储账号信息，避免密码暴露在代码中
- **本地处理**：所有数据仅在本地处理，不会上传到第三方服务器
- **.env 文件安全**：确保 `.env` 文件已添加到 `.gitignore` 中，不会被提交到版本控制
- **临时环境变量**：如果使用环境变量，建议在每次使用时临时设置，而不是永久保存
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
- 优先级 1：⭐
- 优先级 3：⭐⭐  
- 优先级 5：⭐⭐⭐
- 其他：无标记

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
- 发送邮件至：[your-email@example.com]

---

**注意**：本项目仅供学习和个人使用，请遵守滴答清单的服务条款。
