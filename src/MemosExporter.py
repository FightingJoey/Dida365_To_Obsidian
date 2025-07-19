import requests
import os
from Types import MemosRecord
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

def fetch_memos(api_url, token, limit=20, offset=0, rowStatus="NORMAL"):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    params = {
        "limit": limit,
        "offset": offset,
        "rowStatus": rowStatus,
    }
    response = requests.get(api_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    # 格式化为 MemosRecord
    return [MemosRecord(item) for item in data]

def export_weekly_memos_summary(memos, output_dir):
    """
    导出每周 Memos 摘要，按 createdTs 聚合，输出为 Markdown
    """
    if not memos:
        print("没有 Memos 数据")
        return
    # 获取本周起止时间（周一到周日）
    now = datetime.now()
    start_date = now - timedelta(days=now.weekday())
    start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
    end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
    iso_year, week_num, _ = now.isocalendar()
    filename = f"{iso_year}-W{week_num:02d}-Memos.md"
    filepath = os.path.join(output_dir, filename)
    # 按天聚合
    days = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    week_days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    days_with_weekday = [
        f"{week_days[i]}（{(start_date + timedelta(days=i)).strftime('%Y-%m-%d')}）" for i in range(7)
    ]
    memos_by_day = {d: [] for d in days}
    for memo in memos:
        if not memo.createdTs:
            continue
        dt = datetime.fromtimestamp(memo.createdTs)
        if start_date <= dt <= end_date:
            date_str = dt.strftime('%Y-%m-%d')
            if date_str in memos_by_day:
                memos_by_day[date_str].append(memo)
    content = f"# {iso_year} 第 {week_num:02d} 周 Memos 摘要\n\n"
    content += f"**周期**：{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}\n\n"
    for i, day in enumerate(days):
        content += f"## {days_with_weekday[i]}\n\n"
        day_memos = memos_by_day[day]
        if day_memos:
            day_memos_sorted = sorted(day_memos, key=lambda m: m.createdTs or 0)
            for memo in day_memos_sorted:
                dt = datetime.fromtimestamp(memo.createdTs)
                time_str = dt.strftime('%H:%M')
                memo_lines = (memo.content or '').strip().split('\n')
                target_first_line = f"- {time_str} "
                if len(memo_lines) > 1:
                    target_other_line = '\n' + '\n'.join([f"\t{line}" for line in memo_lines])
                else:
                    target_other_line = memo_lines[0] if memo_lines else ''
                content += f"{target_first_line}{target_other_line}\n"
        else:
            content += "无 Memos\n"
        content += "\n"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"已创建每周 Memos 摘要：{filename}")

def export_daily_memos(memos, daily_dir):
    """
    导出每日 Memos，每天一个 Markdown 文件
    """
    if not memos:
        print("没有 Memos 数据")
        return
    # 按天聚合
    memos_by_day = {}
    for memo in memos:
        if not memo.createdTs:
            continue
        dt = datetime.fromtimestamp(memo.createdTs)
        date_str = dt.strftime('%Y-%m-%d')
        if date_str not in memos_by_day:
            memos_by_day[date_str] = []
        memos_by_day[date_str].append(memo)
    for date_str, day_memos in memos_by_day.items():
        if day_memos:
            # 按 createdTs 正序排序
            day_memos_sorted = sorted(day_memos, key=lambda m: m.createdTs or 0)
            filename = f"{date_str}-Memos.md"
            filepath = os.path.join(daily_dir, filename)
            content = ""
            for memo in day_memos_sorted:
                dt = datetime.fromtimestamp(memo.createdTs)
                time_str = dt.strftime('%H:%M')
                memo_lines = (memo.content or '').strip().split('\n')
                target_first_line = f"- {time_str} "
                if len(memo_lines) > 1:
                    target_other_line = '\n' + '\n'.join([f"\t{line}" for line in memo_lines])
                else:
                    target_other_line = memo_lines[0] if memo_lines else ''
                content += f"{target_first_line}{target_other_line}\n"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已创建每日 Memos：{filename}")
        

def main():
    if os.getenv('OUTPUT_DIR'):
        output_dir = os.getenv('OUTPUT_DIR')
    else:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    assert output_dir is not None, "输出目录不能为空"

    memos_dir = os.getenv('MEMOS_DIR', 'Memos')
    api_url = os.getenv('MEMOS_API')
    memos_token = os.getenv('MEMOS_TOKEN')

    daily_dir = os.path.join(output_dir, memos_dir, "1.Daily")
    os.makedirs(daily_dir, exist_ok=True)
    weekly_dir = os.path.join(output_dir, memos_dir, "2.Weekly")
    os.makedirs(weekly_dir, exist_ok=True)

    memos = fetch_memos(api_url, memos_token, limit=10, offset=0, rowStatus="NORMAL")
    export_daily_memos(memos, daily_dir)
    export_weekly_memos_summary(memos, weekly_dir)

if __name__ == "__main__":
    main() 