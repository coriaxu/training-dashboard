from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
import os
import zipfile
import tempfile
from datetime import datetime
from sqlalchemy import desc

from models import db, User, Role, Backup, SystemLog
from utils import get_file_size

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_role('admin'):
            return jsonify({'error': 'Unauthorized'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 用户管理页面
@admin.route('/admin/users')
@login_required
@admin_required
def users():
    department = request.args.get('department')
    role = request.args.get('role')
    search = request.args.get('search')

    query = User.query
    
    if department:
        query = query.filter(User.department == department)
    if role:
        query = query.join(User.roles).filter(Role.name == role)
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    users = query.all()
    all_roles = Role.query.all()
    
    return render_template('admin/users.html', users=users, all_roles=all_roles)

# 用户管理 API
@admin.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'email': user.email,
        'department': user.department,
        'position': user.position,
        'roles': [role.id for role in user.roles]
    })

@admin.route('/api/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    data = request.json
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        department=data.get('department'),
        position=data.get('position')
    )
    user.set_password(data['password'])
    
    # 添加角色
    if 'roles' in data:
        roles = Role.query.filter(Role.id.in_(data['roles'])).all()
        user.roles.extend(roles)
    
    db.session.add(user)
    
    # 记录日志
    SystemLog.log(
        'INFO',
        'User Management',
        'Create User',
        current_user,
        request.remote_addr,
        f'Created user: {user.username}'
    )
    
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

@admin.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    user.email = data['email']
    user.department = data.get('department')
    user.position = data.get('position')
    
    if data.get('password'):
        user.set_password(data['password'])
    
    if 'roles' in data:
        user.roles = []
        roles = Role.query.filter(Role.id.in_(data['roles'])).all()
        user.roles.extend(roles)
    
    SystemLog.log(
        'INFO',
        'User Management',
        'Update User',
        current_user,
        request.remote_addr,
        f'Updated user: {user.username}'
    )
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@admin.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    
    action = 'Activate' if user.is_active else 'Deactivate'
    SystemLog.log(
        'INFO',
        'User Management',
        f'{action} User',
        current_user,
        request.remote_addr,
        f'{action}d user: {user.username}'
    )
    
    db.session.commit()
    return jsonify({'message': 'User status updated successfully'})

@admin.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.username == 'admin':
        return jsonify({'error': 'Cannot delete admin user'}), 400
    
    SystemLog.log(
        'WARN',
        'User Management',
        'Delete User',
        current_user,
        request.remote_addr,
        f'Deleted user: {user.username}'
    )
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})

# 系统管理页面
@admin.route('/admin/system')
@login_required
@admin_required
def system():
    backups = Backup.query.order_by(desc(Backup.created_at)).all()
    logs = SystemLog.query.order_by(desc(SystemLog.timestamp)).limit(100).all()
    return render_template('admin/backup.html', backups=backups, logs=logs)

# 系统管理 API
@admin.route('/api/system/status')
@login_required
@admin_required
def system_status():
    # 获取数据库文件大小
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_size = get_file_size(db_path)
    
    # 获取活跃用户数
    active_users = User.query.filter_by(is_active=True).count()
    
    return jsonify({
        'db_size': db_size,
        'active_users': active_users,
        'uptime': '30 days'  # 这里需要实现实际的运行时间计算
    })

@admin.route('/api/backup/create', methods=['POST'])
@login_required
@admin_required
def create_backup():
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_{timestamp}.zip'
            backup_path = os.path.join(temp_dir, backup_filename)
            
            # 创建 ZIP 文件
            with zipfile.ZipFile(backup_path, 'w') as zipf:
                # 添加数据库文件
                db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                zipf.write(db_path, 'database.db')
                
                # 添加上传的文件
                uploads_dir = current_app.config['UPLOAD_FOLDER']
                if os.path.exists(uploads_dir):
                    for root, _, files in os.walk(uploads_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, uploads_dir)
                            zipf.write(file_path, f'uploads/{arcname}')
            
            # 获取备份文件大小
            backup_size = os.path.getsize(backup_path)
            
            # 移动备份文件到备份目录
            backup_dir = os.path.join(current_app.root_path, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            final_backup_path = os.path.join(backup_dir, backup_filename)
            os.rename(backup_path, final_backup_path)
            
            # 创建备份记录
            backup = Backup(
                filename=backup_filename,
                size=backup_size,
                created_by=current_user,
                description='System backup'
            )
            db.session.add(backup)
            
            SystemLog.log(
                'INFO',
                'System',
                'Create Backup',
                current_user,
                request.remote_addr,
                f'Created backup: {backup_filename}'
            )
            
            db.session.commit()
            
            return jsonify({'message': 'Backup created successfully'})
            
    except Exception as e:
        SystemLog.log(
            'ERROR',
            'System',
            'Create Backup',
            current_user,
            request.remote_addr,
            f'Backup creation failed: {str(e)}'
        )
        return jsonify({'error': str(e)}), 500

@admin.route('/api/backup/<int:backup_id>/download')
@login_required
@admin_required
def download_backup(backup_id):
    backup = Backup.query.get_or_404(backup_id)
    backup_path = os.path.join(current_app.root_path, 'backups', backup.filename)
    
    if not os.path.exists(backup_path):
        return jsonify({'error': 'Backup file not found'}), 404
    
    SystemLog.log(
        'INFO',
        'System',
        'Download Backup',
        current_user,
        request.remote_addr,
        f'Downloaded backup: {backup.filename}'
    )
    
    return send_file(
        backup_path,
        as_attachment=True,
        download_name=backup.filename
    )

@admin.route('/api/backup/<int:backup_id>/restore', methods=['POST'])
@login_required
@admin_required
def restore_backup(backup_id):
    backup = Backup.query.get_or_404(backup_id)
    backup_path = os.path.join(current_app.root_path, 'backups', backup.filename)
    
    if not os.path.exists(backup_path):
        return jsonify({'error': 'Backup file not found'}), 404
    
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压备份文件
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # 恢复数据库
            db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            temp_db_path = os.path.join(temp_dir, 'database.db')
            os.replace(temp_db_path, db_path)
            
            # 恢复上传的文件
            uploads_dir = current_app.config['UPLOAD_FOLDER']
            temp_uploads_dir = os.path.join(temp_dir, 'uploads')
            if os.path.exists(temp_uploads_dir):
                if os.path.exists(uploads_dir):
                    os.rename(uploads_dir, f'{uploads_dir}.bak')
                os.rename(temp_uploads_dir, uploads_dir)
            
            SystemLog.log(
                'INFO',
                'System',
                'Restore Backup',
                current_user,
                request.remote_addr,
                f'Restored backup: {backup.filename}'
            )
            
            return jsonify({'message': 'Backup restored successfully'})
            
    except Exception as e:
        SystemLog.log(
            'ERROR',
            'System',
            'Restore Backup',
            current_user,
            request.remote_addr,
            f'Backup restoration failed: {str(e)}'
        )
        return jsonify({'error': str(e)}), 500

@admin.route('/api/backup/<int:backup_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_backup(backup_id):
    backup = Backup.query.get_or_404(backup_id)
    backup_path = os.path.join(current_app.root_path, 'backups', backup.filename)
    
    # 删除备份文件
    if os.path.exists(backup_path):
        os.remove(backup_path)
    
    SystemLog.log(
        'WARN',
        'System',
        'Delete Backup',
        current_user,
        request.remote_addr,
        f'Deleted backup: {backup.filename}'
    )
    
    db.session.delete(backup)
    db.session.commit()
    
    return jsonify({'message': 'Backup deleted successfully'})

# 系统监控页面
@admin.route('/admin/monitoring')
@login_required
@admin_required
def monitoring():
    return render_template('admin/monitoring.html')

@admin.route('/api/monitoring/data')
@login_required
@admin_required
def monitoring_data():
    from monitoring import get_monitoring_data
    return jsonify(get_monitoring_data())
