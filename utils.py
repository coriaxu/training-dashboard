import os
from datetime import datetime

def get_file_size(file_path):
    """获取文件大小并返回人类可读的格式"""
    if not os.path.exists(file_path):
        return "0 B"
    
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

def get_uptime():
    """获取系统运行时间"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}天 {hours}小时"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"
    except:
        return "未知"

def format_datetime(dt):
    """格式化日期时间"""
    if not dt:
        return ""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def create_directory_if_not_exists(directory):
    """如果目录不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return True
    return False
