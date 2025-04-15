# create_admin.py
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin',
            fullname='Administrator',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('123')
        db.session.add(admin)
        db.session.commit()
        print('Admin mặc định đã được tạo.')
