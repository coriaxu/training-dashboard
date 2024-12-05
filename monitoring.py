import os
import psutil
import platform
from datetime import datetime
from models import User, TrainingSession, TrainingRecord, SystemLog
from sqlalchemy import func, and_

class SystemMonitor:
    @staticmethod
    def get_system_info():
        """获取系统信息"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_total': psutil.disk_usage('/').total
        }
    
    @staticmethod
    def get_resource_usage():
        """获取资源使用情况"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_used': psutil.virtual_memory().used,
            'memory_percent': psutil.virtual_memory().percent,
            'disk_used': psutil.disk_usage('/').used,
            'disk_percent': psutil.disk_usage('/').percent
        }
    
    @staticmethod
    def get_process_info():
        """获取进程信息"""
        process = psutil.Process()
        return {
            'pid': process.pid,
            'memory_used': process.memory_info().rss,
            'cpu_percent': process.cpu_percent(interval=1),
            'threads': process.num_threads(),
            'open_files': len(process.open_files())
        }

class ApplicationMonitor:
    @staticmethod
    def get_user_stats():
        """获取用户统计信息"""
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.join(User.roles).filter_by(name='admin').count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users
        }
    
    @staticmethod
    def get_training_stats():
        """获取培训统计信息"""
        now = datetime.now()
        
        # 获取本月的培训会话数
        monthly_sessions = TrainingSession.query.filter(
            and_(
                func.extract('year', TrainingSession.start_time) == now.year,
                func.extract('month', TrainingSession.start_time) == now.month
            )
        ).count()
        
        # 获取完成的培训记录数
        completed_records = TrainingRecord.query.filter_by(status='completed').count()
        
        # 获取平均培训评分
        avg_rating = db.session.query(
            func.avg(TrainingFeedback.rating)
        ).scalar() or 0
        
        return {
            'monthly_sessions': monthly_sessions,
            'completed_records': completed_records,
            'average_rating': round(float(avg_rating), 2)
        }
    
    @staticmethod
    def get_error_stats():
        """获取错误统计信息"""
        now = datetime.now()
        
        # 获取今日错误日志数
        daily_errors = SystemLog.query.filter(
            and_(
                SystemLog.level == 'ERROR',
                func.date(SystemLog.timestamp) == now.date()
            )
        ).count()
        
        # 获取本月错误日志数
        monthly_errors = SystemLog.query.filter(
            and_(
                SystemLog.level == 'ERROR',
                func.extract('year', SystemLog.timestamp) == now.year,
                func.extract('month', SystemLog.timestamp) == now.month
            )
        ).count()
        
        return {
            'daily_errors': daily_errors,
            'monthly_errors': monthly_errors
        }

class DatabaseMonitor:
    @staticmethod
    def get_table_stats():
        """获取数据库表统计信息"""
        stats = {}
        tables = [User, TrainingSession, TrainingRecord, SystemLog]
        
        for table in tables:
            stats[table.__tablename__] = {
                'total_rows': table.query.count()
            }
        
        return stats
    
    @staticmethod
    def get_db_size():
        """获取数据库文件大小"""
        from flask import current_app
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if os.path.exists(db_path):
            return os.path.getsize(db_path)
        return 0

def get_monitoring_data():
    """获取所有监控数据"""
    return {
        'system': {
            'info': SystemMonitor.get_system_info(),
            'resources': SystemMonitor.get_resource_usage(),
            'process': SystemMonitor.get_process_info()
        },
        'application': {
            'users': ApplicationMonitor.get_user_stats(),
            'training': ApplicationMonitor.get_training_stats(),
            'errors': ApplicationMonitor.get_error_stats()
        },
        'database': {
            'tables': DatabaseMonitor.get_table_stats(),
            'size': DatabaseMonitor.get_db_size()
        },
        'timestamp': datetime.now().isoformat()
    }
