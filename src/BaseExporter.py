import os
from datetime import datetime, timedelta
from typing import Optional
from Types import Task, Project

class BaseExporter:
    """
    导出器基类，包含共用的工具方法和初始化逻辑
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化基础导出器
        
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
    
    def _formate_datetime(self, date: Optional[str]) -> Optional[datetime]:
        if not date:
            return None
        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
        # 转换为北京时间（UTC+8）
        beijing_time = (dt + timedelta(hours=8)).replace(tzinfo=None)
        return beijing_time

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
            beijing_time = self._formate_datetime(time_str)
            if beijing_time:
                return beijing_time.strftime(time_format)
        except (ValueError, AttributeError):
            return None

    def _format_task_time_range(self, task: Task) -> str:
        """
        格式化任务的时间范围
        返回格式：
        - 只有开始时间：📅 从 YYYY-MM-DD 开始
        - 只有结束时间：📅 至 YYYY-MM-DD
        - 有开始和结束时间：📅 YYYY-MM-DD ~ YYYY-MM-DD
        - 没有时间信息：空字符串
        """
        start_date = None
        end_date = None
        
        if task.startDate:
            start_date = self._format_time(task.startDate, "%Y-%m-%d")
        if task.dueDate:
            end_date = self._format_time(task.dueDate, "%Y-%m-%d")
        
        if start_date and end_date:
            if start_date == end_date:
                return f"📅 {start_date}"
            return f"📅 {start_date} ~ {end_date}"
        elif start_date:
            return f"📅 从 {start_date} 开始"
        elif end_date:
            return f"📅 至 {end_date}"
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