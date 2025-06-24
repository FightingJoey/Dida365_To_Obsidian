class Tag:
    """
    标签类，表示滴答清单中的一个标签
    
    包含标签的所有属性，如名称、颜色等，并提供序列化方法
    """
    def __init__(self, task_dict=None):
        """
        初始化标签对象
        
        参数:
            task_dict: 包含标签属性的字典，如果提供则用其初始化标签对象
        """
        # 标签名称
        self.name = None
        # 原始名称（未经处理的名称）
        self.rawName = None
        # 标签标签（可能用于显示）
        self.label = None
        # 排序顺序
        self.sortOrder = None
        # 排序类型
        self.sortType = None
        # 标签颜色
        self.color = None
        # 标签的ETag（用于缓存和并发控制）
        self.etag = None
        # 标签类型
        self.type = None
        
        # 如果提供了字典，则更新对象的属性       
        if task_dict:
            self.__dict__.update(task_dict)
    
    def to_dict(self):
        """
        将标签对象转换为字典，过滤掉值为None的属性
        
        返回:
            dict: 包含标签非空属性的字典
        """
        return {key: value for key, value in self.__dict__.items() if value is not None}        


class Project:
    """
    项目类，表示滴答清单中的一个项目（清单）
    
    包含项目的所有属性，如名称、颜色、权限等，并提供序列化方法
    """
    def __init__(self, task_dict=None):
        """
        初始化项目对象
        
        参数:
            task_dict: 包含项目属性的字典，如果提供则用其初始化项目对象
        """
        # 项目ID
        self.id: str = ''
        # 项目名称
        self.name: str = ''
        # 是否为项目所有者
        self.isOwner = None
        # 项目颜色
        self.color = None
        # 排序顺序
        self.sortOrder = None
        # 排序选项
        self.sortOption = None
        # 排序类型
        self.sortType = None
        # 用户数量
        self.userCount = None
        # 项目的ETag（用于缓存和并发控制）
        self.etag = None
        # 最后修改时间
        self.modifiedTime = None
        # 是否在所有项目中显示
        self.inAll = None
        # 显示类型
        self.showType = None
        # 是否静音通知
        self.muted = None
        # 提醒类型
        self.reminderType = None
        # 是否已关闭
        self.closed = None
        # 是否已转移
        self.transferred = None
        # 组ID
        self.groupId = None
        # 视图模式
        self.viewMode = None
        # 通知选项
        self.notificationOptions = None
        # 团队ID
        self.teamId = None
        # 权限
        self.permission = None
        # 项目类型
        self.kind = None
        # 时间线
        self.timeline = None
        # 是否需要审核
        self.needAudit = None
        # 条形码是否需要审核
        self.barcodeNeedAudit = None
        # 是否对团队开放
        self.openToTeam = None
        # 团队成员权限
        self.teamMemberPermission = None
        # 来源
        self.source = None

        # 如果提供了字典，则更新对象的属性
        if task_dict:
            self.__dict__.update(task_dict)

    def to_dict(self):
        """
        将项目对象转换为字典，过滤掉值为None的属性
        
        返回:
            dict: 包含项目非空属性的字典
        """
        # 返回一个字典，过滤掉值为 None 的属性
        return {key: value for key, value in self.__dict__.items() if value is not None}

class Task:
    """
    任务类，表示滴答清单中的一个任务
    
    包含任务的所有属性，如标题、截止日期、优先级等，并提供序列化方法
    """
    def __init__(self, task_dict=None):
        """
        初始化任务对象
        
        参数:
            task_dict: 包含任务属性的字典，如果提供则用其初始化任务对象
        """
        # 任务唯一标识符（字符串格式，如"681473bbf92b2938d3ab5d45"）
        self.id = None  
        
        # 任务标题（字符串，必填字段）
        self.title = None  
        
        # 所属项目ID（字符串，如"6778eeb7c71c710000000114"表示特定项目）
        self.projectId = None  
        
        # 开始时间（ISO 8601格式字符串，如"2025-05-21T16:00:00.000+0000"）
        self.startDate = None  
        
        # 子任务列表（数组，存储子任务对象，默认空数组）
        self.items = []
        
        # 提醒时间列表（数组，存储提醒时间点，默认空数组）
        self.reminders = None  
        
        # 排除的重复日期（数组，存储重复任务中跳过的时间点，默认空数组）
        self.exDate = None  
        
        # 截止时间（ISO 8601格式字符串，可为None表示无截止时间）
        self.dueDate = None  
        
        # 优先级（整数1-5，5最高，0表示无优先级）
        self.priority = None  
        
        # 是否为全天任务（布尔值，True表示全天任务）
        self.isAllDay = None  
        
        # 重复规则（字符串，如"RRULE:FREQ=DAILY"，None表示不重复）
        self.repeatFlag = None  
        
        # 进度百分比（整数0-100，0表示未开始）
        self.progress = None  
        
        # 任务负责人（用户ID，None表示无人负责）
        self.assignee = None  
        
        # 排序权重（数值越小越靠前，通常为大负数）
        self.sortOrder = None  
        
        # 是否为浮动时间（布尔值，True表示忽略时区）
        self.isFloating = None  
        
        # 任务状态（整数：0=未完成，2=已完成，-1=已放弃）
        self.status = None  
        
        # 任务类型扩展字段（保留字段，通常为None）
        self.kind = None  
        
        # 创建时间（ISO 8601格式字符串）
        self.createdTime = None  
        
        # 最后修改时间（ISO 8601格式字符串）
        self.modifiedTime = None  

        # 任务完成时间（ISO 8601格式字符串）
        self.completedTime = None
        
        # 标签列表（数组，存储字符串类型的标签）
        self.tags = None  
        
        # 时区标识（字符串，如"Asia/Hong_Kong"）
        self.timeZone = None  
        
        # 任务描述内容（字符串，可为空）
        self.content = None  

        self.childIds = []

        self.parentId = ''

        # 如果有输入字典，覆盖对应字段
        if task_dict:
            self.__dict__.update(task_dict)
    
    def to_dict(self):
        """
        将任务对象转换为字典，过滤掉值为None的属性
        
        返回:
            dict: 包含任务非空属性的字典
        """
        return {key: value for key, value in self.__dict__.items() if value is not None}        

class Habit:
    """
    习惯类，表示滴答清单中的一个习惯
    包含习惯的所有属性，如名称、颜色、打卡次数、提醒等，并提供序列化方法
    """
    def __init__(self, habit_dict=None):
        """
        初始化习惯对象
        参数:
            habit_dict: 包含习惯属性的字典，如果提供则用其初始化习惯对象
        """
        # 习惯ID
        self.id = None
        # 习惯名称
        self.name = None
        # 图标资源名
        self.iconRes = None
        # 习惯颜色
        self.color = None
        # 排序顺序
        self.sortOrder = None
        # 状态（0=启用，1=归档）
        self.status = None
        # 鼓励语
        self.encouragement = None
        # 总打卡次数
        self.totalCheckIns = None
        # 创建时间（ISO 8601字符串）
        self.createdTime = None
        # 修改时间（ISO 8601字符串）
        self.modifiedTime = None
        # 归档时间（ISO 8601字符串）
        self.archivedTime = None
        # 类型（如 Boolean）
        self.type = None
        # 目标值
        self.goal = None
        # 步长
        self.step = None
        # 单位
        self.unit = None
        # etag
        self.etag = None
        # 重复规则（如 RRULE:FREQ=WEEKLY...）
        self.repeatRule = None
        # 提醒时间列表
        self.reminders = None
        # 是否启用记录（字符串 'True'/'False'）
        self.recordEnable = None
        # 分区ID
        self.sectionId = None
        # 目标天数
        self.targetDays = None
        # 目标开始日期（如 20250403）
        self.targetStartDate = None
        # 已完成周期数
        self.completedCycles = None
        # 排除日期
        self.exDates = None
        # 风格（如 1）
        self.style = None
        # 如果提供了字典，则更新对象的属性
        if habit_dict:
            self.__dict__.update(habit_dict)
    
    def to_dict(self):
        """
        将习惯对象转换为字典，过滤掉值为None的属性
        返回:
            dict: 包含习惯非空属性的字典
        """
        return {key: value for key, value in self.__dict__.items() if value is not None}
