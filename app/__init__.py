from flask import Flask
from config import Config
from app.extensions import db, login_manager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

def create_app():   
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your-secret-key'  # BẮT BUỘC PHẢI CÓ
    
    csrf.init_app(app)  # Bật CSRF bảo vệ toàn app

    # Khởi tạo extensions
    db.init_app(app)
    login_manager.init_app(app)
    # Cấu hình Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    Migrate(app, db)

    # Import blueprints
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp

    # Đăng ký blueprints
    app.register_blueprint(auth_bp)                 # => /, /login, /logout
    app.register_blueprint(admin_bp, url_prefix='/admin')  # => /admin/dashboard, ...

    return app
