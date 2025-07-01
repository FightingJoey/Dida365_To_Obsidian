import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from Dida365Client import Dida365Client
from Types import Task, Project, Habit
from BaseExporter import BaseExporter

class CalendarExporter(BaseExporter):
    """
    日历导出器，用于创建基于时间的任务摘要
    支持按日、周、月导出任务摘要到对应目录
    """
    
    def __init__(self, client: Dida365Client, output_dir: Optional[str] = None):
        """
        初始化日历导出器
        
        参数:
            client: Dida365Client 实例
            output_dir: 输出目录，如果不提供则从环境变量 OUTPUT_DIR 获取，如果都没有则使用当前目录
        """
        super().__init__(output_dir)
        
        assert self.output_dir is not None, "输出目录不能为空"

        self.client = client
        
        # 创建日历相关目录
        calendar_dir = os.getenv('CALENDAR_DIR', 'Calendar')
        self.calendar_dir = os.path.join(self.output_dir, calendar_dir)
        self.daily_dir = os.path.join(self.calendar_dir, "1.Daily")
        self.weekly_dir = os.path.join(self.calendar_dir, "2.Weekly")
        self.monthly_dir = os.path.join(self.calendar_dir, "3.Monthly")
        
        # 确保所有目录存在
        for dir_path in [self.calendar_dir, self.daily_dir, self.weekly_dir, self.monthly_dir]:
            self._ensure_dir(dir_path)

    def _get_tasks(self, sources, status: int, start_date: datetime, end_date: datetime) -> List[Task]:
        tasks = []
        for task_data in sources:
            if task_data:
                task = Task(task_data)
                # 只处理已完成的任务
                if task.status == status:
                        should_include = self._task_in_range(task, start_date, end_date)
                        if should_include:
                            tasks.append(task)
        return tasks

    def _get_tasks_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """
        获取指定日期范围内的任务（包括待办和已完成）
        
        一个任务会被包含在结果中，如果：
        1. 任务在日期范围内开始
        2. 任务在日期范围内结束
        3. 任务的时间跨度覆盖了该日期范围
        
        注意：没有任何时间信息（既没有开始时间也没有截止时间）的任务将被忽略
        """        
        # 获取所有未完成任务
        response = self.client.get_all_data()
        todo_tasks = response.get("syncTaskBean", {}).get("update", [])
        # 处理未完成任务数据
        todos = self._get_tasks(todo_tasks, 0, start_date, end_date)
        
        # 获取已完成任务
        completed_tasks = self.client.get_completed_tasks(
            from_date=start_date.strftime("%Y-%m-%d %H:%M:%S"),
            to_date=end_date.strftime("%Y-%m-%d %H:%M:%S")
        )
        # 处理已完成任务
        completeds = self._get_tasks(completed_tasks, 2, start_date, end_date)
        
        return todos + completeds
    
    def _task_in_range(self, task: Task, start: datetime, end: datetime) -> bool:
        """判断任务是否在指定时间范围内（用于月摘要的周分组）"""
        # 使用 _formate_datetime 获取任务的开始时间和结束时间
        task_start = self._formate_datetime(task.startDate)
        task_end = self._formate_datetime(task.dueDate)
        
        if not task_start and not task_end:
            return False
        if task_start and task_end:
            return not (task_end < start or task_start > end)
        elif task_start:
            return task_start <= end
        elif task_end:
            return task_end >= start
        return False

    def _format_task_line(self, task: Task, index: Optional[int] = None, ordered: bool = False) -> str:
        """格式化单个任务行。待办任务可用有序数字列表。"""
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
    
    def export_daily_summary(self, date: Optional[datetime] = None):
        """
        导出每日任务摘要
        
        参数:
            date: 指定日期，如果不提供则使用当前日期
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
        content = f"# {date.strftime('%Y-%m-%d')} 摘要\n\n"

        # 获取习惯数据
        habits_data = self.client.get_habits()
        habits = []
        if isinstance(habits_data, list):
            for h in habits_data:
                habit = Habit(h)
                if getattr(habit, 'status', None) == 0:
                    habits.append(habit)
        # 计算 stamp（前一天）
        prev_day = start_date - timedelta(days=1)
        stamp = prev_day.strftime("%Y%m%d")
        # 获取 habit_ids
        habit_ids = [habit.id for habit in habits]
        # 获取 checkins
        checkins = self.client.get_habits_checkins(stamp, habit_ids)
        # 获取当天的 stamp
        today_stamp = int(start_date.strftime("%Y%m%d"))
        
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
        """
        if date is None:
            date = datetime.now()
        date = date.replace(tzinfo=None)
        start_date = date - timedelta(days=date.weekday())
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        tasks = self._get_tasks_in_date_range(start_date, end_date)
        filename = f"{start_date.strftime('%Y-W%W')}-Dida365.md"
        filepath = os.path.join(self.weekly_dir, filename)
        content = f"# {start_date.strftime('%Y')} 第 {start_date.strftime('%W')} 周任务摘要\n\n"
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
                    task_date = self._formate_datetime(task.completedTime)
                elif task.dueDate:
                    task_date = self._formate_datetime(task.dueDate)
                elif task.startDate:
                    task_date = self._formate_datetime(task.startDate)
                if task_date:
                    date_str = task_date.strftime('%Y-%m-%d')
                    if date_str in tasks_by_day:
                        tasks_by_day[date_str].append(task)
            for i, day in enumerate(days):
                content += f"## {days_with_weekday[i]}\n\n"
                day_tasks = tasks_by_day[day]
                if day_tasks:
                    # 先输出代办，再输出已完成
                    todos = [t for t in day_tasks if t.status == 0]
                    dones = [t for t in day_tasks if t.status == 2]
                    todos_sorted = sorted(todos, key=lambda x: -(x.priority if x.priority else 0))
                    dones_sorted = sorted(dones, key=lambda x: -(x.priority if x.priority else 0))
                    all_tasks = todos_sorted + dones_sorted
                    # 表头
                    content += "| 序号 | 任务 | 优先级 | 时间范围 | 状态 | 完成时间 |\n"
                    content += "| --- | --- | --- | --- | --- | --- |\n"
                    for idx, task in enumerate(all_tasks, 1):
                        title = f"[[{task.id}\|{task.title}]]"
                        priority = self._get_priority_mark(task.priority if task.priority else 0)
                        time_range = self._format_task_time_range(task)
                        status = "待办" if task.status == 0 else "已完成"
                        done_time = self._format_time(task.completedTime, "%Y-%m-%d") if task.status == 2 else ""
                        content += f"| {idx} | {title} | {priority} | {time_range} | {status} | {done_time} |\n"
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
        content = f"# {date.strftime('%Y-%m')} 月任务摘要\n\n"
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
                    todos = [t for t in week_tasks if t.status == 0]
                    dones = [t for t in week_tasks if t.status == 2]
                    todos_sorted = sorted(todos, key=lambda x: -(x.priority if x.priority else 0))
                    dones_sorted = sorted(dones, key=lambda x: -(x.priority if x.priority else 0))
                    all_tasks = todos_sorted + dones_sorted
                    # 表头
                    content += "| 序号 | 任务 | 优先级 | 时间范围 | 状态 | 完成时间 |\n"
                    content += "| --- | --- | --- | --- | --- | --- |\n"
                    for idx, task in enumerate(all_tasks, 1):
                        title = f"[[{task.id}\|{task.title}]]"
                        priority = self._get_priority_mark(task.priority if task.priority else 0)
                        time_range = self._format_task_time_range(task)
                        status = "待办" if task.status == 0 else "已完成"
                        done_time = self._format_time(task.completedTime, "%Y-%m-%d") if task.status == 2 else ""
                        content += f"| {idx} | {title} | {priority} | {time_range} | {status} | {done_time} |\n"
                else:
                    content += "无任务\n"
                content += "\n"
        else:
            content += "本月没有任务。\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已创建每月摘要：{filename}")


# 使用示例
if __name__ == "__main__":
    try:
        # 初始化客户端
        client = Dida365Client()
        
        # 创建日历导出器
        exporter = CalendarExporter(client)
        
        # 导出当前的日、周、月摘要
        today = datetime.now()
        exporter.export_daily_summary(today)
        exporter.export_weekly_summary(today)
        exporter.export_monthly_summary(today)
        
    except ValueError as e:
        print(f"环境变量配置错误: {e}")
        exit(1)
    except Exception as e:
        print(f"导出失败: {e}")
        exit(1) 