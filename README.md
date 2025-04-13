# Project1_flask_management

Web Quản Lý Công Việc Nhóm
Chức năng chính:
CRUD thành viên, task, deadline
Phân quyền (Admin phân công, user cập nhật tiến độ)
Upload file báo cáo
Hiển thị tiến độ công việc dạng biểu đồ
Nâng cao:
Gửi email nhắc nhở deadline
Giao diện realtime cập nhật trạng thái task

# Flask Team Management Application Scaffold
# Directory structure:
#
# flask_team_management/
# ├── app/
# │   ├── __init__.py
# │   ├── models.py
# │   ├── forms.py
# │   ├── routes.py
# │   ├── email.py
# │   ├── templates/
# │   │   ├── base.html
# │   │   ├── index.html
# │   │   ├── login.html
# │   │   ├── register.html
# │   │   ├── members/
# │   │   ├── tasks/
# │   │   └── ...
# │   └── static/
# │       ├── css/
# │       ├── js/
# │       └── uploads/
# ├── migrations/
# ├── venv/
# ├── config.py
# ├── requirements.txt
# └── run.py

# requirements.txt
# ----------------
# Flask
# Flask-SQLAlchemy
# Flask-Migrate
# Flask-Login
# Flask-Mail
# Flask-WTF
# Flask-SocketIO
# eventlet
# APScheduler
# python-dotenv
# chart.js (via CDN)