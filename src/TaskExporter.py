import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dotenv import load_dotenv
from Dida365Client import Dida365Client
from Types import Task, Project
from BaseExporter import BaseExporter

# 加载 .env 文件
load_dotenv()

class TaskExporter(BaseExporter):
    def __init__(self, client: Dida365Client, output_dir: Optional[str] = None, unified_index: bool = True):
        """
        初始化任务导出器
        
        参数:
            client: Dida365Client 实例
            output_dir: markdown 文件输出目录，如果不提供则从环境变量 OUTPUT_DIR 获取，如果都没有则使用当前目录
            unified_index: 是否只生成一个统一的项目索引文件 AllProjects.md ，所有项目内容都写入该文件，默认 True
        """
        super().__init__(output_dir)
        assert self.output_dir is not None, "输出目录不能为空"

        self.client = client
        self.unified_index = unified_index
        
        task_dir = os.getenv('TASKS_DIR', 'Tasks')
        self.tasks_dir = os.path.join(self.output_dir, task_dir)
        project_dir = os.getenv('PROJECTS_DIR', 'Projects')
        self.project_dir = os.path.join(self.output_dir, project_dir)
        tasks_inbox_path = os.getenv('TASKS_INBOX_PATH', 'TasksInbox.md')
        self.tasks_inbox_path = os.path.join(self.output_dir, tasks_inbox_path)
        
        # 确保输出目录存在
        self._ensure_dir(self.tasks_dir)
        if not self.unified_index:
            self._ensure_dir(self.project_dir)
    
    def export_project_tasks(self, project_id: str = ''):
        """
        导出所有项目的未完成任务
        
        参数:
            project_id: 项目ID，如果提供则只导出该项目的任务
        """
        projects = []
        tasks = []

        if self.client.inbox_id:
            inbox = Project()
            inbox.id = self.client.inbox_id
            inbox.name = "收集箱"
            projects.append(inbox)

        response = self.client.get_all_data()
        
        # 处理项目数据
        for i in response.get("projectProfiles", []):
            if i != []:
                projects.append(Project(i))
        # 处理任务数据
        for i in response.get("syncTaskBean", {}).get("update", []):
            if i != []:
                tasks.append(Task(i))

        # 筛选未完成的任务
        unfinished_tasks = [task for task in tasks if task.status == 0]
        
        # 构建 id->Task 映射
        task_dict = {task.id: task for task in unfinished_tasks}
        
        # 如果指定了项目ID，只处理该项目
        if project_id:
            projects = [p for p in projects if p.id == project_id]
            if not projects:
                print(f"未找到项目: {project_id}")
                return
        
        # 统一索引模式
        if self.unified_index:
            all_content = ""
            for project in projects:
                # 获取该项目下的未完成任务
                project_tasks = [task for task in unfinished_tasks if task.projectId == project.id]
                all_content += self._get_project_index_content(project, project_tasks)
            index_path = self.tasks_inbox_path
            if os.path.exists(index_path):
                os.remove(index_path)
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(all_content)
            print(f"已创建统一项目索引文件: TasksInbox.md")
            # 依然导出单个任务文件
            for project in projects:
                project_tasks = [task for task in unfinished_tasks if task.projectId == project.id]
                for task in project_tasks:
                    self._create_task_markdown(task, task_dict)
        else:
            # 原有分项目索引逻辑
            for project in projects:
                # 获取该项目下的未完成任务
                project_tasks = [task for task in unfinished_tasks if task.projectId == project.id]
                self._create_project_index(project, project_tasks, self.project_dir)
                for task in project_tasks:
                    self._create_task_markdown(task, task_dict)
    
    def _create_project_index(self, project: Project, tasks: List[Task], project_dir: str):
        """
        创建项目索引文件
        
        参数:
            project: Project 对象
            tasks: 项目任务列表
            project_dir: 项目目录路径
        """
        filename = f"{project.name}.md"
        index_path = os.path.join(project_dir, filename)
        
        # 准备 Front Matter
        front_matter = {
            "title": f"{project.name}",
            "project_id": project.id,
            "updated_time": self._format_time(datetime.now().isoformat())
        }
        
        # 构建文件内容
        content = "---\n"
        for key, value in front_matter.items():
            if value is not None:
                content += f"{key}: {value}\n"
        content += "---\n\n"
        
        # 添加项目信息
        content += f"# {project.name}\n\n"
        
        # 添加任务列表
        if tasks:
            content += "## 任务列表\n\n"
            # 按优先级和创建时间排序
            sorted_tasks = sorted(tasks, 
                                key=lambda x: (-x.priority if x.priority else 0, 
                                             x.createdTime if x.createdTime else ""))
            
            for task in sorted_tasks:
                priority_mark = self._get_priority_mark(task.priority if task.priority else 0)
                time_range = self._format_task_time_range(task)
                if time_range == "":
                    content += f"- [ ] [[{task.id}|{task.title}]] | {priority_mark}\n"
                else:
                    content += f"- [ ] [[{task.id}|{task.title}]] | {priority_mark} | {time_range}\n"
        
        # 写入文件
        # 如果文件存在，先删除
        if os.path.exists(index_path):
            os.remove(index_path)
            print(f"删除旧文件: {project.name}")

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已创建项目索引文件: {project.name}.md")
    
    def _create_task_markdown(self, task: Task, task_dict: Dict[str, Task]):
        """
        为单个任务创建或更新 markdown 文件
        
        参数:
            task: Task 对象
            task_dict: 所有未完成任务的 id->Task 映射
        """
        # 构建文件名
        filename = f"{task.id}.md"
        filepath = os.path.join(self.tasks_dir, filename)
        
        # 检查文件是否存在
        file_exists = os.path.exists(filepath)
        
        # 如果文件存在，检查是否需要更新
        if file_exists:
            # 读取现有文件的 Front Matter 中的 modified_time
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # 查找 Front Matter 中的 modified_time
                import re
                match = re.search(r'modified_time:\s*(.*?)(?:\n|$)', content)
                if match:
                    file_modified_time = match.group(1).strip()
                    # 如果文件中的修改时间与任务修改时间相同，则跳过
                    if file_modified_time == self._format_time(task.modifiedTime):
                        print(f"任务文件已是最新: {filename}")
                        return
        
        # 准备 Front Matter
        front_matter = {
            "title": task.title,
            "task_id": task.id,
            "project_id": task.projectId,
            "start_date": self._format_time(task.startDate),
            "due_date": self._format_time(task.dueDate),
            "priority": task.priority,
            "status": task.status,
            "created_time": self._format_time(task.createdTime),
            "modified_time": self._format_time(task.modifiedTime),
            "completedTime": self._format_time(task.completedTime)
        }
        
        # 构建文件内容
        content = "---\n"
        for key, value in front_matter.items():
            if value is not None:
                content += f"{key}: {value}\n"
        content += "---\n\n"
        
        # 添加任务描述
        if task.content:
            content += f"{task.content}\n\n"
        
        # 添加任务列表
        if task.items:
            content += "## 任务列表\n\n"
            for item in task.items:
                status = "✓" if item.get("status") == 1 else " "
                content += f"- [{status}] {item.get('title', '')}\n"

        # 添加子任务列表
        if task.childIds:
            content += "## 子任务列表\n\n"
            content += "| 任务标题 | 优先级 | 截止日期 |\n"
            content += "| --- | --- | --- |\n"
            for childId in task.childIds:
                child_task = task_dict.get(childId)
                if child_task:
                    child_title = child_task.title
                    child_priority = child_task.priority
                    priority_mark = self._get_priority_mark(child_priority if child_priority else 0)
                    child_due_date = self._format_time(child_task.dueDate, "%Y-%m-%d")
                    content += f"| [[{childId}|{child_title}]] | {priority_mark} | {child_due_date} |\n"
        
        # 添加父任务
        if task.parentId:
            content += f"## 父任务\n\n"
            content += "| 任务标题 | 优先级 | 截止日期 |\n"
            content += "| --- | --- | --- |\n"
            parent_task = task_dict.get(task.parentId)
            parent_title = parent_task.title if parent_task and getattr(parent_task, 'title', None) else None
            parent_priority = parent_task.priority if parent_task and getattr(parent_task, 'priority', None) else None
            priority_mark = self._get_priority_mark(parent_priority if parent_priority else 0)
            parent_due_date = self._format_time(parent_task.dueDate, "%Y-%m-%d") if parent_task and getattr(parent_task, 'dueDate', None) else None
            content += f"| [[{task.parentId}|{parent_title}]] | {priority_mark} | {parent_due_date} |\n"
        
        # 写入文件
        # 如果文件存在，先删除
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"删除旧文件: {filename}")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已创建任务文件: {filename}")

    def _get_project_index_content(self, project: Project, tasks: List[Task]) -> str:
        """
        返回某个项目的索引内容（不写入文件，仅返回字符串）
        """
        content = f"# {project.name}\n\n"
        if tasks:
            sorted_tasks = sorted(tasks, key=lambda x: (-x.priority if x.priority else 0, x.createdTime if x.createdTime else ""))
            for task in sorted_tasks:
                priority_mark = self._get_priority_mark(task.priority if task.priority else 0)
                time_range = self._format_task_time_range(task)
                if time_range == "":
                    content += f"- [ ] [[{task.id}|{task.title}]] | {priority_mark}\n"
                else:
                    content += f"- [ ] [[{task.id}|{task.title}]] | {priority_mark} | {time_range}\n"
        content += "\n"
        return content

# 使用示例
if __name__ == "__main__":
    # 方法1：使用环境变量（推荐）
    # 设置环境变量：
    # export DIDA365_USERNAME="your_email@example.com"
    # export DIDA365_PASSWORD="your_password"
    try:
        # 初始化客户端
        client = Dida365Client()
        
        # 创建导出器并执行导出
        exporter = TaskExporter(client)
        
        # 导出所有项目的任务
        exporter.export_project_tasks()
        
    except ValueError as e:
        print(f"环境变量配置错误: {e}")
        print("请设置以下环境变量：")
        print("export DIDA365_USERNAME=\"your_email@example.com\"")
        print("export DIDA365_PASSWORD=\"your_password\"")
        exit(1)
    except Exception as e:
        print(f"导出失败: {e}")
        exit(1)
    
    # 方法2：直接传入参数（不推荐，密码会暴露在代码中）
    # client = Dida365Client(
    #     username="your_email@example.com",
    #     password="your_password"
    # )
    # exporter = TaskExporter(client, "/path/to/output")
    # exporter.export_project_tasks()
    