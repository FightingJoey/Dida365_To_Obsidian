import requests
import json
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv, set_key

# 加载 .env 文件
load_dotenv()

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")

class Dida365Client:
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        初始化滴答清单客户端
        
        参数:
            username: 用户名/邮箱，如果不提供则从环境变量 DIDA365_USERNAME 读取
            password: 密码，如果不提供则从环境变量 DIDA365_PASSWORD 读取
        """
        # 从环境变量或参数获取账号信息
        self.username = username or os.getenv('DIDA365_USERNAME')
        self.password = password or os.getenv('DIDA365_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError(
                "请提供账号信息。可以通过参数传入或设置环境变量：\n"
                "DIDA365_USERNAME: 你的滴答清单用户名/邮箱\n"
                "DIDA365_PASSWORD: 你的滴答清单密码\n"
                "或者创建 .env 文件并设置这些变量"
            )
        
        self.base_url = "https://api.dida365.com/api/v2"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "x-device": "{\"platform\":\"web\",\"os\":\"Windows 10\",\"device\":\"Chrome 136.0.0.0\",\"name\":\"\",\"version\":6246,\"id\":\"66c5c4f4efae8477e84eb688\",\"channel\":\"website\",\"campaign\":\"\",\"websocket\":\"67e7de9bf92b296c741567e0\"}"
        }
        self.token = None
        self.inbox_id = None
        # 优先尝试从 .env 读取 token
        self._load_token_from_env()
        if not self.token:
            print("登录获取Token")
            self.login(self.username, self.password)
        else:
            print("使用本地保存的Token")
            self.headers["Cookie"] = f"t={self.token}"

    def _load_token_from_env(self):
        self.token = os.getenv("DIDA365_TOKEN")
        self.inbox_id = os.getenv("DIDA365_INBOX_ID")
        if self.token == "None":
            self.token = None
        if self.inbox_id == "None":
            self.inbox_id = None

    def _save_token_to_env(self):
        # 更新 .env 文件中的 DIDA365_TOKEN
        try:
            set_key(ENV_FILE, "DIDA365_TOKEN", self.token)
            set_key(ENV_FILE, "DIDA365_INBOX_ID", self.inbox_id)
        except Exception as e:
            print(f"保存 token 到 .env 失败: {e}")

    def login(self, username: str, password: str):
        """登录获取token"""
        url = f"{self.base_url}/user/signon?wc=true&remember=true"
        payload = {
            "password": password,
            "username": username
        }
        response = requests.request(
            "POST",
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["token"]
        self.inbox_id = data["inboxId"]
        # 在后续请求中设置Cookie
        self.headers["Cookie"] = f"t={self.token}"
        self._save_token_to_env()

    def _make_request(self, method: str, endpoint: str, params=None, data=None) -> Dict:
        """通用的请求方法"""
        url = f"{self.base_url}/{endpoint}"
        # 处理URL中的路径变量
        url = url.replace("${projectId}", params.get("projectId", "")) if params else url
        url = url.replace("${taskId}", params.get("taskId", "")) if params else url
        response = requests.request(
            method,
            url,
            headers=self.headers,
            params=params,
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_projects(self) -> Dict:
        """获取所有的项目列表"""
        return self._make_request("GET", "projects")
    
    def get_all_data(self) -> Dict:
        """获取项目列表、任务列表、标签列表"""
        return self._make_request("GET", "batch/check/0")
    
    def get_project_tasks(self, project_id: str, to_date: str, limit: int = 50) -> Dict:
        """获取项目中的任务列表"""
        params = {
            "from": "",
            "to": to_date,
            "limit": limit
        }
        return self._make_request("GET", f"project/{project_id}/completed/", params=params)
    
    def get_task(self, task_id: str) -> Dict:
        """获取任务信息"""
        return self._make_request("GET", f"task/{task_id}")
    
    def get_completed_tasks(self, from_date: str, to_date: str, limit: int = 50) -> Dict:
        """获取已完成任务列表"""
        params = {
            "from": from_date,
            "to": to_date,
            "limit": limit
        }
        return self._make_request("GET", "project/all/completed", params=params)
    
    def get_abandoned_tasks(self, status: str = "Abandoned", limit: int = 10) -> Dict:
        """获取已放弃任务列表"""
        params = {
            "from": "",
            "to": "",
            "status": status,
            "limit": limit
        }
        return self._make_request("GET", "project/all/closed", params=params)
    
    def get_task_comments(self, project_id: str, task_id: str) -> Dict:
        """获取任务的评论内容"""
        params = {
            "projectId": project_id,
            "taskId": task_id
        }
        return self._make_request("GET", "project/${projectId}/task/${taskId}/comments", params=params)
    
    def get_trash_tasks(self) -> Dict:
        """获取垃圾箱内的任务列表"""
        return self._make_request("GET", "project/all/trash/pagination")
    
    def get_habits(self) -> Dict:
        """获取习惯列表"""
        return self._make_request("GET", "habits")

# 使用示例
if __name__ == "__main__":
    # 方法1：使用环境变量（推荐）
    # 设置环境变量：
    # export DIDA365_USERNAME="your_email@example.com"
    # export DIDA365_PASSWORD="your_password"
    try:
        client = Dida365Client()
    except ValueError as e:
        print(f"环境变量配置错误: {e}")
        exit(1)
    
    # 方法2：直接传入参数（不推荐，密码会暴露在代码中）
    # client = Dida365Client(
    #     username="your_email@example.com",
    #     password="your_password"
    # )
    
    try:
        # 获取所有项目
        projects = client.get_projects()
        print(f"获取到 {len(projects)} 个项目")
        
        # 获取第一个项目ID
        if projects:
            first_project_id = projects[0]["id"]
            
            # 获取项目任务
            tasks = client.get_project_tasks(
                project_id=first_project_id,
                to_date="2025-06-08 15:50:23"
            )
            print(f"获取到 {len(tasks)} 个任务")
            
            # 获取习惯列表
            habits = client.get_habits()
            print(f"获取到 {len(habits)} 个习惯")
    except Exception as e:
        print(f"API 调用失败: {e}")