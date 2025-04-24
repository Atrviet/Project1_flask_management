from flask import Flask
from config import Config
from app.extensions import db, login_manager, mail, init_scheduler, socketio
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

csrf = CSRFProtect()

def create_app():   
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'your-secret-key' 
    
    csrf.init_app(app) 

    # Gắn SQLAlchemy với app
    db.init_app(app)
    # Gắn Flask-Login để xử lý login/logout
    login_manager.init_app(app)

    # Cấu hình Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    # Gắn SocketIO
    socketio.init_app(app, cors_allowed_origins="*")

    Migrate(app, db)

    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.member.routes import member_bp

    # Đăng ký blueprints
    app.register_blueprint(auth_bp)                 # => /, /login, /logout
    app.register_blueprint(admin_bp, url_prefix='/admin')  # => /admin/dashboard, ...
    app.register_blueprint(member_bp, url_prefix='/member')
    
    # Gắn Flask-Mail và scheduler
    mail.init_app(app)
    init_scheduler(app)

    return app
