from app import server, db
from models import User

def init_database():
    with server.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建管理员账户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Created admin user')
        
        print('Database initialized successfully')
