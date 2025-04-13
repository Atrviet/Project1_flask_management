from flask import Flask
from app.extensions import db, login_manager
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo extensions với app
    db.init_app(app)
    login_manager.init_app(app)

    # Import routes SAU KHI khởi tạo extensions
    from app.routes import auth_bp, admin_bp

    # Đăng ký blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app