import os
from datetime import datetime, timedelta
from typing import Optional

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
        
        # 确保 output_dir 不为 None
        assert self.output_dir is not None, "输出目录不能为空"
    
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
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            # 转换为北京时间（UTC+8）
            beijing_time = dt + timedelta(hours=8)
            return beijing_time.strftime(time_format)
        except (ValueError, AttributeError):
            return None

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