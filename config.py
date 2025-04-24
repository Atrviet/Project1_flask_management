# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Tải biến môi trường từ file .env

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Cấu hình bảo mật & DB
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///team_management.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'app', 'static', 'uploads')

    # Cấu hình Flask-Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('FLASK TEAM MANAGEMENT', os.environ.get('MAIL_USERNAME'))
