# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_apscheduler import APScheduler


# Khởi tạo các extensions (chưa gắn với app)
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")
scheduler = APScheduler()

# Đăng ký user_loader
from app.models import Member

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def init_extensions(app):
    """
    Gắn các extensions với Flask app và khởi động scheduler
    """
    db.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    scheduler.init_app(app)
    scheduler.start()


def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()

# app/__init__.py  
from flask import Flask
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from config import Config
from app.extensions import init_extensions, socketio

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    print("App created:", app)
    app.config.from_object(Config)
    print("Config loaded:", app.config)
    app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'change-this')

    # CSRF
    csrf.init_app(app)
    init_extensions(app) # Gắn tất cả các extension ở trên với app

    # Gắn các extension cơ bản (DB, Login, Mail, SocketIO, Scheduler)
    init_extensions(app)

    # Migrate (sử dụng SQLAlchemy đã init xong)
    Migrate(app, app.extensions['sqlalchemy'].db)

    # Đăng ký blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.member.routes import member_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(member_bp)

    return app

