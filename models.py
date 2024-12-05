from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# 用户角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
    department = db.Column(db.String(80))
    position = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    training_records = db.relationship('TrainingRecord', backref='trainee', lazy='dynamic')
    uploaded_records = db.relationship('TrainingRecord', backref='uploader', lazy='dynamic', foreign_keys='TrainingRecord.uploaded_by')
    feedback = db.relationship('TrainingFeedback', backref='trainee', lazy='dynamic')
    backups = db.relationship('Backup', backref='created_by', lazy=True)
    system_logs = db.relationship('SystemLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON)

class Backup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    size = db.Column(db.Integer)  # 文件大小(字节)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', backref=db.backref('backups', lazy=True))
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default='completed')  # completed, failed

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(10))  # INFO, WARN, ERROR
    module = db.Column(db.String(50))
    action = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('system_logs', lazy=True))
    ip_address = db.Column(db.String(50))
    details = db.Column(db.Text)

    @staticmethod
    def log(level, module, action, user=None, ip_address=None, details=None):
        log = SystemLog(
            level=level,
            module=module,
            action=action,
            user=user,
            ip_address=ip_address,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log

class CourseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('course_category.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联
    courses = db.relationship('Course', backref='category', lazy='dynamic')
    subcategories = db.relationship('CourseCategory', backref=db.backref('parent', remote_side=[id]))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('course_category.id'))
    duration = db.Column(db.Float)  # 课程时长（小时）
    max_participants = db.Column(db.Integer)  # 最大参与人数
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联
    training_sessions = db.relationship('TrainingSession', backref='course', lazy='dynamic')

class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80))
    specialization = db.Column(db.String(200))
    contact = db.Column(db.String(100))
    bio = db.Column(db.Text)
    is_internal = db.Column(db.Boolean, default=True)  # 内部/外部讲师
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联
    training_sessions = db.relationship('TrainingSession', backref='trainer', lazy='dynamic')

class TrainingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20))  # 计划中/进行中/已完成/已取消
    max_participants = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联
    records = db.relationship('TrainingRecord', backref='session', lazy='dynamic')
    attendance = db.relationship('TrainingAttendance', backref='session', lazy='dynamic')

class TrainingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('training_session.id'), nullable=False)
    status = db.Column(db.String(20))  # 已报名/已完成/未完成/已取消
    completion_date = db.Column(db.DateTime)
    certificate_id = db.Column(db.String(100))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 关联
    feedback = db.relationship('TrainingFeedback', backref='record', lazy='dynamic')
    attendance = db.relationship('TrainingAttendance', backref='record', lazy='dynamic')

class TrainingAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('training_record.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('training_session.id'), nullable=False)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # 出勤/迟到/早退/缺勤
    created_at = db.Column(db.DateTime, default=datetime.now)

class TrainingFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('training_record.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_rating = db.Column(db.Integer)  # 1-5分
    trainer_rating = db.Column(db.Integer)  # 1-5分
    organization_rating = db.Column(db.Integer)  # 1-5分
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('training_record.id'), nullable=False)
    certificate_no = db.Column(db.String(100), unique=True)
    issue_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # 有效/已过期/已撤销
    created_at = db.Column(db.DateTime, default=datetime.now)

class SystemBackup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    backup_type = db.Column(db.String(50))  # 完整备份/增量备份
    size = db.Column(db.Integer)  # 文件大小(bytes)
    status = db.Column(db.String(20))  # 成功/失败
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
