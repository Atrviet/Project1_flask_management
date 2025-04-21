import os
import random
from io import BytesIO
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, session, send_file, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Member
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__)

# --- Thiết lập đường dẫn đến thư mục Data chứa ảnh CAPTCHA ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'Data')


@auth_bp.route('/captcha_image')
def captcha_image():
    """Serve ảnh captcha hiện tại từ session"""
    filename = session.get('captcha_filename')
    if not filename:
        abort(404)
    path = os.path.join(DATA_DIR, filename)
    if not os.path.isfile(path):
        abort(404)
    with open(path, 'rb') as f:
        img_bytes = f.read()
    return send_file(
        BytesIO(img_bytes),
        mimetype='image/png',
        as_attachment=False,
        download_name=filename
    )


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('member.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    # Lấy next param từ query string (GET) hoặc form (POST)
    next_arg = request.args.get('next', '')

    # GET: tạo captcha và hiển thị form
    if request.method == 'GET':
        files = [f for f in os.listdir(DATA_DIR)
                 if os.path.isfile(os.path.join(DATA_DIR, f))]
        session['captcha_filename'] = random.choice(files) if files else ''
        return render_template('auth/login.html', form=form, next=next_arg)

    # POST: xác thực captcha
    current_filename = session.get('captcha_filename', '')
    expected_code = os.path.splitext(current_filename)[0].strip().lower()
    user_input = (form.captcha.data or '').strip().lower()
    if user_input != expected_code:
        flash('Mã captcha không đúng.', 'danger')
        return render_template('auth/login.html', form=form, next=request.form.get('next', ''))

    # Xác thực user
    user = User.query.filter_by(username=form.username.data).first()
    if user and user.check_password(form.password.data):
        login_user(user, remember=form.remember_me.data)
        print('>>> AUTHENTICATED:', current_user.is_authenticated)
        flash('Đăng nhập thành công!', 'success')

        next_page = request.form.get('next') or next_arg

        # Nếu next_page là trang login thì bỏ qua
        if next_page and '/login' not in next_page:
            return redirect(next_page)
        print('>>> NEXT PAGE:', next_page)
        # Redirect về next nếu có
        if next_page:
            return redirect(next_page)
        # Chuyển hướng theo role nếu không có next
        print('>>> ROLE:', current_user.role)
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('member.dashboard'))

    flash('Sai thông tin đăng nhập.', 'danger')
    return render_template('auth/login.html', form=form, next=request.form.get('next', next_arg))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
