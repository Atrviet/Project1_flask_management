from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Khởi tạo extensions nhưng chưa gắn với app
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'