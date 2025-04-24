from datetime import datetime, date
from flask_login import UserMixin
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    fullname = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Quan hệ ngược với TaskLog và ProgressFeedback
    task_logs = db.relationship(
        'TaskLog', back_populates='user', lazy=True, cascade='all, delete-orphan'
    )
    feedbacks = db.relationship(
        'ProgressFeedback', back_populates='admin', lazy=True, cascade='all, delete-orphan'
    )
    
# Member Model
class Member(db.Model):
    __tablename__ = 'members'

    # Khóa chính đồng thời là khóa ngoại đến users.id
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.String(20), nullable=True)

    # Quan hệ trở lại User và Task
    user = db.relationship('User', backref=db.backref('member', uselist=False))
    tasks = db.relationship(
        'Task', back_populates='assignee_member', lazy=True, cascade='all, delete-orphan'
    )

# Task Model
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file = db.Column(db.String(255))
    file_data = db.Column(db.LargeBinary)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(32), nullable=False, default='New')
    progress = db.Column(db.Integer, nullable=False, default=0)

    # Khóa ngoại đến Member
    assignee_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    assignee_member = db.relationship(
        'Member', back_populates='tasks'
    )

    # Quan hệ với TaskLog và Progress
    logs = db.relationship(
        'TaskLog', back_populates='task', lazy=True, cascade='all, delete-orphan'
    )
    progress_entries = db.relationship(
        'Progress', back_populates='task', lazy=True, cascade='all, delete-orphan'
    )

# TaskLog Model lưu nhật ký tiến độ
class TaskLog(db.Model):
    __tablename__ = 'task_logs'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    description = db.Column(db.Text, nullable=False)
    progress = db.Column(db.Integer, nullable=False)

    # Quan hệ hai chiều
    task = db.relationship('Task', back_populates='logs')
    user = db.relationship('User', back_populates='task_logs')


# Progress Model tóm tắt tiến độ
class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    description = db.Column(db.Text, nullable=False)

    # Quan hệ hai chiều
    task = db.relationship('Task', back_populates='progress_entries')
    user = db.relationship('User')

# ProgressFeedback Model đánh giá admin
class ProgressFeedback(db.Model):
    __tablename__ = 'progress_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    progress_id = db.Column(db.Integer, db.ForeignKey('progress.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # Quan hệ hai chiều
    progress = db.relationship('Progress', back_populates='feedbacks')
    admin = db.relationship('User', back_populates='feedbacks')

# Thiết lập back_populates cho Progress -> ProgressFeedback
Progress.feedbacks = db.relationship(
    'ProgressFeedback', back_populates='progress', lazy=True, cascade='all, delete-orphan'
)
