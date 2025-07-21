import os
from Dida365Client import Dida365Client
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from Types import Task, Project, Habit
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Exporter:
    
    def __init__(self, projects, todo_tasks, completed_tasks, output_dir: Optional[str] = None):
        """
        初始化导出器
        
        参数:
            output_dir: 输出目录，如果不提供则从环境变量 OUTPUT_DIR 获取，如果都没有则使用当前目录
        """
        # 确定输出目录：参数 > 环境变量 > 当前目录
        if output_dir:
            self.output_dir = output_dir
        elif os.getenv('OUTPUT_DIR'):
            self.output_dir = os.getenv('OUTPUT_DIR')
        else:
            self.output_dir = os.path.dirname(os.path.abspath(__file__))
        
        assert self.output_dir is not None, "输出目录不能为空"

        self.projects = projects
        self.todo_tasks = todo_tasks
        self.completed_tasks = completed_tasks
        
        # 创建日历相关目录
        calendar_dir = os.getenv('CALENDAR_DIR', 'Calendar')
        self.calendar_dir = os.path.join(self.output_dir, calendar_dir)
        self.daily_dir = os.path.join(self.calendar_dir, "1.Daily")
        self.weekly_dir = os.path.join(self.calendar_dir, "2.Weekly")
        self.monthly_dir = os.path.join(self.calendar_dir, "3.Monthly")

        # 任务相关目录
        task_dir = os.getenv('TASKS_DIR', 'Tasks')
        self.tasks_dir = os.path.join(self.output_dir, task_dir)
        tasks_inbox_dir = os.getenv('TASKS_INBOX_PATH', 'Inbox')
        self.tasks_inbox_dir = os.path.join(self.output_dir, tasks_inbox_dir)
        self.tasks_inbox_path = os.path.join(self.tasks_inbox_dir, 'TasksInbox.md')
        
        # 确保所有目录存在
        for dir_path in [self.calendar_dir, self.daily_dir, self.weekly_dir, self.monthly_dir, self.tasks_dir, self.tasks_inbox_dir]:
            self._ensure_dir(dir_path)

    def _format_time(self, time_str: Optional[str], time_format: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
        """
        将时间字符串格式化为北京时间
        
        参数:
            time_str: ISO 格式的时间字符串
            time_format: 输出的时间格式
            
        返回:
            格式化后的时间字符串
        """
        if not time_str:
            return None
            
        try:
            # 处理 ISO 格式的时间字符串
            beijing_time = formate_datetime(time_str)
            if beijing_time:
                return beijing_time.strftime(time_format)
        except (ValueError, AttributeError):
            return None

    def _format_task_time_range(self, task: Task) -> str:
        """
        格式化任务的时间范围为易读的字符串格式
        
        根据任务的开始时间和截止时间，生成不同格式的时间范围字符串：
        - 只有开始时间：📅 从 YYYY-MM-DD 开始
        - 只有结束时间：📅 至 YYYY-MM-DD
        - 有开始和结束时间：📅 YYYY-MM-DD ~ YYYY-MM-DD
        - 开始和结束时间相同：📅 YYYY-MM-DD
        - 没有时间信息：空字符串
        
        参数:
            task: Task 对象，包含 startDate 和 dueDate 属性（可能是 datetime 对象或字符串）
            
        返回:
            格式化后的时间范围字符串
        """
        start_date = None
        end_date = None
        
        # 优先使用处理后的时间，如果没有则使用原始时间
        start_time = getattr(task, '_processed_startDate', None) or task.startDate
        end_time = getattr(task, '_processed_dueDate', None) or task.dueDate
        
        # 处理 startDate（可能是 datetime 对象或字符串）
        if start_time:
            if isinstance(start_time, datetime):
                start_date = start_time.strftime("%Y-%m-%d")
            else:
                start_date = self._format_time(start_time, "%Y-%m-%d")
        
        # 处理 dueDate（可能是 datetime 对象或字符串）
        if end_time:
            if isinstance(end_time, datetime):
                end_date = end_time.strftime("%Y-%m-%d")
            else:
                end_date = self._format_time(end_time, "%Y-%m-%d")
        
        if start_date and end_date:
            if start_date == end_date:
                return f"📅 {end_date}"
            return f"🛫 {start_date} ~ 📅 {end_date}"
        elif start_date:
            return f"🛫 {start_date}"
        elif end_date:
            return f"📅 {end_date}"
        return ""

    def _get_priority_mark(self, priority: int) -> str:
        """
        获取优先级标记
        
        参数:
            priority: 优先级值
            
        返回:
            对应的优先级表情符号
        """
        if priority == 1:
            return "🔽"
        elif priority == 3:
            return "🔼"
        elif priority == 5:
            return "⏫"
        else:
            return "⏬"
    
    def _ensure_dir(self, dir_path: str):
        """
        确保目录存在，如果不存在则创建
        
        参数:
            dir_path: 目录路径
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path) 

    def _create_task_markdown(self, task: Task, task_dict: Dict[str, Task]):
        """
        为单个任务创建或更新 Markdown 文件
        
        该方法会根据任务信息创建或更新对应的 Markdown 文件，包括：
        1. 检查文件是否存在，如存在则检查是否需要更新
        2. 生成包含任务详细信息的 Front Matter
        3. 添加任务描述内容
        4. 添加任务列表（如果有）
        5. 添加子任务列表（如果有）
        6. 添加父任务信息（如果有）
        
        参数:
            task: Task 对象，包含任务的所有信息
            task_dict: 所有任务的 id->Task 映射，用于查找父任务和子任务
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
            "start_date": self._format_time_from_task(getattr(task, '_processed_startDate', None) or task.startDate),
            "due_date": self._format_time_from_task(getattr(task, '_processed_dueDate', None) or task.dueDate),
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
            content += self._create_table_header()
            for childId in task.childIds:
                child_task = task_dict.get(childId)
                if child_task:
                    content += self._create_task_table_content(child_task)
        
        # 添加父任务
        if task.parentId:
            content += f"## 父任务\n\n"
            content += self._create_table_header()
            parent_task = task_dict.get(task.parentId)
            if parent_task:
                content += self._create_task_table_content(parent_task)
        
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
        
        该方法生成项目的索引内容，包括：
        1. 项目标题
        2. 按优先级排序的任务列表，每个任务包含链接、优先级标记和时间范围
        
        参数:
            project: Project 对象，包含项目信息
            tasks: 该项目下的任务列表
            
        返回:
            格式化后的项目索引内容字符串
        """
        content = f"## {project.name}\n\n"
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
    
    def _get_tasks(self, sources, start_date: datetime, end_date: datetime) -> List[Task]:
        """
        从任务源中筛选出指定时间范围内的任务
        
        参数:
            sources: 任务源列表
            start_date: 开始日期
            end_date: 结束日期
            
        返回:
            在指定时间范围内的任务列表
        """
        tasks = []
        for task in sources:
            should_include = self._task_in_range(task, start_date, end_date)
            if should_include:
                tasks.append(task)
        return tasks

    def _task_in_range(self, task: Task, start: datetime, end: datetime) -> bool:
        """
        判断任务是否在指定时间范围内（用于月摘要的周分组）
        
        一个任务被认为在时间范围内，如果满足以下任一条件：
        1. 任务的开始时间和结束时间都在范围内
        2. 任务的开始时间在范围内（无结束时间）
        3. 任务的结束时间在范围内（无开始时间）
        4. 任务的时间跨度覆盖了该范围
        
        参数:
            task: 要检查的任务
            start: 时间范围的开始时间
            end: 时间范围的结束时间
            
        返回:
            如果任务在指定时间范围内，则返回 True，否则返回 False
        """
        # 优先使用处理后的时间，如果没有则使用原始时间
        task_start = getattr(task, '_processed_startDate', None) or task.startDate
        task_end = getattr(task, '_processed_dueDate', None) or task.dueDate
        
        # 获取任务的开始时间和结束时间（可能是 datetime 对象或字符串）
        start_dt = None
        end_dt = None
        
        if task_start:
            if isinstance(task_start, datetime):
                start_dt = task_start
            else:
                start_dt = formate_datetime(task_start)
        
        if task_end:
            if isinstance(task_end, datetime):
                end_dt = task_end
            else:
                end_dt = formate_datetime(task_end)
        
        if not start_dt and not end_dt:
            return False
        if start_dt and end_dt:
            return not (end_dt < start or start_dt > end)
        elif start_dt:
            return start_dt <= end
        elif end_dt:
            return end_dt >= start
        return False

    def _get_tasks_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """
        获取指定日期范围内的任务（包括待办和已完成）
        
        一个任务会被包含在结果中，如果：
        1. 任务在日期范围内开始
        2. 任务在日期范围内结束
        3. 任务的时间跨度覆盖了该日期范围
        
        注意：没有任何时间信息（既没有开始时间也没有截止时间）的任务将被忽略
        """        
        # 处理未完成任务
        todos = self._get_tasks(self.todo_tasks, start_date, end_date)
        
        # 处理已完成任务
        completeds = self._get_tasks(self.completed_tasks, start_date, end_date)
        
        return todos + completeds   

    def _format_task_line(self, task: Task, index: Optional[int] = None, ordered: bool = False) -> str:
        """
        格式化单个任务行为 Markdown 格式
        
        根据任务状态和参数生成不同格式的任务行：
        1. 对于待办任务，可以使用有序数字列表（如果 ordered=True）
        2. 对于已完成任务，添加完成标记和完成日期
        3. 所有任务都包含任务标题链接、优先级标记和时间范围（如果有）
        
        参数:
            task: 要格式化的任务
            index: 任务索引，用于有序列表
            ordered: 是否使用有序列表格式
            
        返回:
            格式化后的任务行字符串
        """
        priority_mark = self._get_priority_mark(task.priority if task.priority else 0)
        time_range = self._format_task_time_range(task)
        if ordered and index is not None:
            line = f"{index}. [[{task.id}|{task.title}]] | {priority_mark}"
        else:
            checkbox = "x" if task.status == 2 else " "
            line = f"- [{checkbox}] [[{task.id}|{task.title}]] | {priority_mark}"
        if time_range:
            line += f" | {time_range}"
        # 对于已完成任务，添加 ✅ 和完成日期
        if task.status == 2:
            done_date = self._format_time(task.completedTime, "%Y-%m-%d")
            line += f" | ✅ {done_date}"
        return line
    
    def _get_summary_front_matter(self) -> str:
        """
        获取摘要的 Front Matter
        
        生成包含更新时间的 Front Matter，用于日/周/月摘要文件
        
        返回:
            格式化后的 Front Matter 字符串
        """
        # 准备 Front Matter
        front_matter = {
            "updated_time": self._format_time(datetime.now().isoformat())
        }
        
        # 构建文件内容
        content = "---\n"
        for key, value in front_matter.items():
            if value is not None:
                content += f"{key}: {value}\n"
        content += "---\n\n"
        return content

    def _format_time_from_task(self, time_value) -> Optional[str]:
        """
        从任务的时间字段格式化时间字符串
        
        参数:
            time_value: 可能是 datetime 对象或字符串的时间值
            
        返回:
            格式化后的时间字符串
        """
        if not time_value:
            return None
        
        if isinstance(time_value, datetime):
            return time_value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return self._format_time(time_value)

    def _create_table_header(self):
        content = "| 任务 | 优先级 | 时间范围 | 状态 | 完成时间 |\n"
        content += "| --- | --- | --- | --- | --- |\n"
        return content

    def _create_task_table_content(self, task: Task):
        content = ""
        title = f"[[{task.id}\|{task.title}]]"
        priority = self._get_priority_mark(task.priority if task.priority else 0)
        time_range = self._format_task_time_range(task)
        status = "待办" if task.status == 0 else "已完成"
        done_time = self._format_time(task.completedTime, "%Y-%m-%d") if task.status == 2 else ""
        content += f"| {title} | {priority} | {time_range} | {status} | {done_time} |\n"
        return content

    def _create_sub_task_table(self, tasks: list[Task]):
        content = ""
        todos = [t for t in tasks if t.status == 0]
        dones = [t for t in tasks if t.status == 2]
        todos_sorted = sorted(todos, key=lambda x: -(x.priority if x.priority else 0))
        dones_sorted = sorted(dones, key=lambda x: -(x.priority if x.priority else 0))
        all_tasks = todos_sorted + dones_sorted
        # 表头
        content += self._create_table_header()
        for task in all_tasks:
            content += self._create_task_table_content(task)
        return content
    # MARK: - 公开方法

    def export_project_tasks(self):
        """
        导出所有项目的未完成任务
        
        该方法执行以下操作：
        1. 构建所有任务的 id->Task 映射
        2. 为每个未完成任务创建 Markdown 文件
        3. 创建统一的项目索引文件，包含所有项目及其任务
        4. 为已完成任务创建 Markdown 文件
        """
        total_tasks = self.todo_tasks + self.completed_tasks
        # 构建 id->Task 映射
        task_dict = {task.id: task for task in total_tasks}
        
        # 准备 Front Matter
        front_matter = {
            "updated_time": self._format_time(datetime.now().isoformat())
        }
        
        # 构建文件内容
        all_content = "---\n"
        for key, value in front_matter.items():
            if value is not None:
                all_content += f"{key}: {value}\n"
        all_content += "---\n\n"
        
        for project in self.projects:
            # 获取该项目下的未完成任务
            project_tasks = [task for task in self.todo_tasks if task.projectId == project.id]
            for task in project_tasks:
                self._create_task_markdown(task, task_dict)
            all_content += self._get_project_index_content(project, project_tasks)
        index_path = self.tasks_inbox_path
        if os.path.exists(index_path):
            os.remove(index_path)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(all_content)
        print(f"已创建统一项目索引文件: TasksInbox.md")

        # 导出已完成任务
        for task in self.completed_tasks:
            self._create_task_markdown(task, task_dict)
    
    def export_daily_summary(self, date: Optional[datetime] = None, habits: Optional[List[Habit]] = None, checkins: Optional[dict] = None, today_stamp: Optional[int] = None):
        """
        导出每日任务摘要
        
        该方法生成指定日期的任务摘要，包括：
        1. 习惯打卡情况（如果提供了习惯数据）
        2. 待办任务列表（按优先级排序）
        3. 已完成任务列表（按优先级排序）
        
        参数:
            date: 指定日期，如果不提供则使用当前日期
            habits: 习惯列表，用于生成习惯打卡部分
            checkins: 习惯打卡记录，用于检查习惯是否已完成
            today_stamp: 当天的时间戳，用于匹配打卡记录
        """
        if date is None:
            date = datetime.now()
            # 确保日期对象不带时区信息
            date = date.replace(tzinfo=None)
        
        # 设置日期范围
        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
        
        # 获取当日任务
        tasks = self._get_tasks_in_date_range(start_date, end_date)
        
        # 创建文件名
        filename = f"{date.strftime('%Y-%m-%d')}-Dida365.md"
        filepath = os.path.join(self.daily_dir, filename)
        # 准备文件内容
        content = self._get_summary_front_matter()
        content += f"# {date.strftime('%Y-%m-%d')} 摘要\n\n"

        # 添加习惯打卡
        if habits:
            content += "## 习惯打卡\n\n"
            done_date = ""
            for habit in habits:
                checked = False
                if checkins and 'checkins' in checkins and habit.id in checkins['checkins']:
                    for c in checkins['checkins'][habit.id]:
                        if c.get('checkinStamp') == today_stamp and c.get('status') == 2:
                            checked = True
                            done_date = self._format_time(c.get('checkinTime'), "%Y-%m-%d")
                            break
                if checked:
                    content += f"- [x] {habit.name} | ✅ {done_date}\n"
                else:
                    content += f"- [ ] {habit.name}\n"
            content += "\n"
        
        if tasks:
            # 分离待办和已完成任务
            todo_tasks = [t for t in tasks if t.status == 0]
            done_tasks = [t for t in tasks if t.status == 2]
            # 输出待办任务
            if todo_tasks:
                content += "## 待办任务\n\n"
                # 按优先级排序
                sorted_tasks = sorted(todo_tasks, key=lambda x: (-(x.priority if x.priority else 0)))
                for idx, task in enumerate(sorted_tasks, 1):
                    content += self._format_task_line(task, idx, ordered=True) + "\n"
                content += "\n"
            # 输出已完成任务
            if done_tasks:
                content += "## 已完成任务\n\n"
                # 按优先级排序
                sorted_tasks = sorted(done_tasks, key=lambda x: (-(x.priority if x.priority else 0)))
                for task in sorted_tasks:
                    content += self._format_task_line(task) + "\n"
                content += "\n"
        else:
            content += "今日没有任务。\n"
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已创建每日摘要：{filename}")
    
    def export_weekly_summary(self, date: Optional[datetime] = None):
        """
        导出每周任务摘要（以日期为节点，每天聚合所有任务，输出为 Markdown 表格）
        
        该方法生成指定周的任务摘要，包括：
        1. 确定周的开始和结束日期
        2. 获取该周内的所有任务
        3. 按天聚合任务
        4. 为每天生成任务表格，包含任务标题、优先级、时间范围、状态和完成时间
        
        参数:
            date: 指定日期，如果不提供则使用当前日期
        """
        if date is None:
            date = datetime.now()
            date = date.replace(tzinfo=None)
        start_date = date - timedelta(days=date.weekday())
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        tasks = self._get_tasks_in_date_range(start_date, end_date)
        # 修正周数计算：使用 isocalendar()
        iso_year, week_num, _ = date.isocalendar()  # 返回 (ISO年份, 周数, 周几)
        filename = f"{iso_year}-W{week_num:02d}-Dida365.md"  # 格式化为两位数周数
        filepath = os.path.join(self.weekly_dir, filename)
        content = self._get_summary_front_matter()
        content += f"# {iso_year} 第 {week_num:02d} 周任务摘要\n\n"
        content += f"**周期**：{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}\n\n"
        if tasks:
            days = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
            week_days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            days_with_weekday = [
                f"{week_days[i]}（{(start_date + timedelta(days=i)).strftime('%Y-%m-%d')}）" for i in range(7)
            ]
            tasks_by_day = {d: [] for d in days}
            for task in tasks:
                task_date = None
                if task.status == 2 and getattr(task, 'completedTime', None):
                    task_date = formate_datetime(task.completedTime)
                elif getattr(task, '_processed_dueDate', None) or task.dueDate:
                    # 优先使用处理后的时间
                    task_date = getattr(task, '_processed_dueDate', None) or formate_datetime(task.dueDate)
                elif getattr(task, '_processed_startDate', None) or task.startDate:
                    # 优先使用处理后的时间
                    task_date = getattr(task, '_processed_startDate', None) or formate_datetime(task.startDate)
                if task_date:
                    date_str = task_date.strftime('%Y-%m-%d')
                    if date_str in tasks_by_day:
                        tasks_by_day[date_str].append(task)
            for i, day in enumerate(days):
                content += f"## {days_with_weekday[i]}\n\n"
                day_tasks = tasks_by_day[day]
                if day_tasks:
                    # 先输出待办，再输出已完成
                    content += self._create_sub_task_table(day_tasks)
                else:
                    content += "无任务\n"
                content += "\n"
        else:
            content += "本周没有任务。\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已创建每周摘要：{filename}")

    def export_monthly_summary(self, date: Optional[datetime] = None):
        """
        导出每月任务摘要（以周为节点，每周聚合所有任务，输出为 Markdown 表格）
        
        该方法生成指定月份的任务摘要，包括：
        1. 确定月份的开始和结束日期
        2. 获取该月内的所有任务
        3. 将月份划分为多个周
        4. 按周聚合任务
        5. 为每周生成任务表格，包含任务标题、优先级、时间范围、状态和完成时间
        
        参数:
            date: 指定日期，如果不提供则使用当前日期
        """
        if date is None:
            date = datetime.now()
            date = date.replace(tzinfo=None)
        start_date = datetime(date.year, date.month, 1)
        if date.month == 12:
            end_date = datetime(date.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(date.year, date.month + 1, 1) - timedelta(seconds=1)
        tasks = self._get_tasks_in_date_range(start_date, end_date)
        filename = f"{date.strftime('%Y-%m')}-Dida365.md"
        filepath = os.path.join(self.monthly_dir, filename)
        content = self._get_summary_front_matter()
        content += f"# {date.strftime('%Y-%m')} 月任务摘要\n\n"
        if tasks:
            first_day = start_date
            last_day = end_date
            weeks = []
            cur = first_day
            while cur <= last_day:
                week_start = cur - timedelta(days=cur.weekday())
                week_start = datetime(week_start.year, week_start.month, week_start.day, 0, 0, 0)
                week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
                if week_start > last_day:
                    break
                weeks.append((week_start, min(week_end, last_day)))
                cur = week_end + timedelta(seconds=1)
            for week_start, week_end in weeks:
                week_num = week_start.strftime('%W')
                content += f"## 第 {week_num} 周 ({week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')})\n\n"
                week_tasks = [t for t in tasks if self._task_in_range(t, week_start, week_end)]
                if week_tasks:
                    content += self._create_sub_task_table(week_tasks)
                else:
                    content += "无任务\n"
                content += "\n"
        else:
            content += "本月没有任务。\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已创建每月摘要：{filename}")

def formate_datetime(date: Optional[str]) -> Optional[datetime]:
        """
        将 ISO 格式的时间字符串转换为北京时间的 datetime 对象
        
        参数:
            date: ISO 格式的时间字符串，例如 '2023-01-01T12:00:00Z'
            
        返回:
            转换后的 datetime 对象，如果输入为空则返回 None
        """
        if not date:
            return None
        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
        # 转换为北京时间（UTC+8）
        beijing_time = (dt + timedelta(hours=8)).replace(tzinfo=None)
        return beijing_time

def get_tasks(client, date):
    """
    获取滴答清单中的项目和任务数据
    
    该函数执行以下操作：
    1. 获取所有项目数据
    2. 获取所有未完成任务
    3. 获取当月已完成的任务
    4. 对任务的时间字段进行预处理和格式化
    
    参数:
        client: Dida365Client 实例，用于与滴答清单 API 交互
        date: 日期对象，用于确定获取已完成任务的时间范围
        
    返回:
        三元组 (projects, todo_tasks, completed_tasks)，分别为项目列表、待办任务列表和已完成任务列表
    """
    response = client.get_all_data()

    projects = []
    todo_tasks = []
    completed_tasks = []

    # 添加收集箱项目
    if client.inbox_id:
        inbox = Project()
        inbox.id = client.inbox_id
        inbox.name = "收集箱"
        projects.append(inbox)

    # 处理项目数据
    for i in response.get("projectProfiles", []):
        if i != []:
            projects.append(Project(i))
    
    # 处理待办任务数据
    for i in response.get("syncTaskBean", {}).get("update", []):
        if i != []:
            task = Task(i)
            if task.status == 0:
                # 预处理时间字段
                preprocess_task_dates(task)
                todo_tasks.append(task)

    # 计算当月的开始和结束日期
    start_date = datetime(date.year, date.month, 1)
    if date.month == 12:
        end_date = datetime(date.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(date.year, date.month + 1, 1) - timedelta(seconds=1)

    # 获取本月已完成任务
    response = client.get_completed_tasks(
        from_date=start_date.strftime("%Y-%m-%d %H:%M:%S"),
        to_date=end_date.strftime("%Y-%m-%d %H:%M:%S")
    )
    for task_data in response:
        if task_data:
            task = Task(task_data)
            if task.status == 2:
                # 预处理时间字段
                preprocess_task_dates(task)
                completed_tasks.append(task)

    return projects, todo_tasks, completed_tasks

def preprocess_task_dates(task: Task):
    """
    预处理任务的时间字段
    
    对任务的 startDate 和 dueDate 进行格式化处理：
    1. 使用 formate_datetime 将 ISO 字符串转换为 datetime 对象
    2. 对于 isAllDay 为 true 的任务，dueDate 需要减一天
    3. 将处理后的 datetime 对象存储为临时属性
    
    参数:
        task: Task 对象，需要预处理时间字段的任务
    """
    
    # 处理 startDate
    if task.startDate:
        processed_start = formate_datetime(task.startDate)
        # 使用 setattr 动态添加属性
        setattr(task, '_processed_startDate', processed_start)
    
    # 处理 dueDate
    if task.dueDate:
        dt = formate_datetime(task.dueDate)
        # 如果是全天任务，dueDate 需要减一天
        if getattr(task, 'isAllDay', False) and task.startDate != task.dueDate and dt:
            dt = dt - timedelta(days=1)
        # 使用 setattr 动态添加属性
        setattr(task, '_processed_dueDate', dt)

def get_habits(client, date):
    """
    获取滴答清单中的习惯数据和打卡记录
    
    该函数执行以下操作：
    1. 获取所有活跃的习惯数据
    2. 获取习惯的打卡记录
    3. 计算当天的时间戳，用于匹配打卡记录
    
    参数:
        client: Dida365Client 实例，用于与滴答清单 API 交互
        date: 日期对象，用于确定获取习惯打卡记录的时间范围
        
    返回:
        三元组 (habits, checkins, today_stamp)，分别为习惯列表、打卡记录和当天时间戳
    """
    # 设置日期范围
    start_date = datetime(date.year, date.month, date.day)

    # 获取习惯数据
    habits_data = client.get_habits()
    habits = []
    if isinstance(habits_data, list):
        for h in habits_data:
            habit = Habit(h)
            # 只保留状态为活跃的习惯
            if getattr(habit, 'status', None) == 0:
                habits.append(habit)
    
    # 计算 stamp（前一天）- 滴答清单 API 需要前一天的时间戳作为参数
    prev_day = start_date - timedelta(days=1)
    stamp = prev_day.strftime("%Y%m%d")
    
    # 获取所有习惯的 ID
    habit_ids = [habit.id for habit in habits]
    
    # 获取习惯打卡记录
    checkins = client.get_habits_checkins(stamp, habit_ids)
    
    # 获取当天的时间戳，用于匹配打卡记录
    today_stamp = int(start_date.strftime("%Y%m%d"))

    return habits, checkins, today_stamp

if __name__ == "__main__":
    # 初始化滴答清单客户端
    client = Dida365Client()
    
    # 获取当前日期（不带时区信息）
    date = datetime.now()
    date = date.replace(tzinfo=None)

    # 获取任务和项目数据
    projects, todo_tasks, completed_tasks = get_tasks(client, date)
    
    # 获取习惯数据和打卡记录
    habits, checkins, today_stamp = get_habits(client, date)

    # 初始化导出器并执行导出操作
    exporter = Exporter(projects, todo_tasks, completed_tasks)
    
    # 导出项目任务到 Markdown 文件
    exporter.export_project_tasks()
    
    # 导出每日任务摘要
    exporter.export_daily_summary(date, habits, checkins, today_stamp)
    
    # 导出每周任务摘要
    exporter.export_weekly_summary(date)
    
    # 导出每月任务摘要
    exporter.export_monthly_summary(date)