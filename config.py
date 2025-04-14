import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình ứng dụng
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')  # Sử dụng SECRET_KEY từ môi trường
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///team_management.db')  # Kết nối cơ sở dữ liệu
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Tắt theo dõi các thay đổi không cần thiết

# Cấu hình Flask với SQLAlchemy và Migrate
app.config.from_object(Config)

# Khởi tạo SQLAlchemy và Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)
