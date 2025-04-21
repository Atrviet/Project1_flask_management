from datetime import datetime
from flask_login import UserMixin
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    fullname = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    
    def set_password(self, password):
        """Sinh password_hash từ mật khẩu gốc."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """So sánh mật khẩu gốc với hash đã lưu."""
        return check_password_hash(self.password_hash, password)

    # Thiết lập quan hệ một-nhất với Member
    member = db.relationship('Member', back_populates='user', uselist=False)

class Member(db.Model):
    __tablename__ = 'members'

    # Khóa chính đồng thời là khóa ngoại đến users.id
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    # Ví dụ thêm thông tin mở rộng cho member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.String(20), nullable=True)

    # Liên kết trở lại User
    user = db.relationship('User', back_populates='member')

    # Quan hệ một-nhiều với Task
    tasks = db.relationship('Task', back_populates='assignee_member', cascade='all, delete-orphan')

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file = db.Column(db.String(255))
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(32), nullable=False, default='New')
    progress = db.Column(db.Integer, nullable=False, default=0)

    # Thay đổi khóa ngoại để liên kết đến bảng members
    assignee_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)

    # Quan hệ trở lại Member
    assignee_member = db.relationship('Member', back_populates='tasks')
