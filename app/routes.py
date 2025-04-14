from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Admin, Member  # Thêm import Member
from app.forms import LoginForm, RegisterMemberForm  # Thêm import RegisterMemberForm
from .forms import LoginForm

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

@auth_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Route cho trang đăng nhập
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Tạo đối tượng form từ LoginForm
    if form.validate_on_submit():  # Kiểm tra khi người dùng submit
        username = form.username.data
        password = form.password.data
        user = Admin.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Đăng nhập thất bại. Vui lòng kiểm tra lại tên đăng nhập hoặc mật khẩu.', 'danger')

    return render_template('login.html', form=form)  # Truyền form vào template

# Route cho trang đăng xuất
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Kiểm tra quyền admin bằng cách kiểm tra 'role'
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập vào trang này.', 'danger')
        return redirect(url_for('auth.login'))  # Chuyển hướng về trang đăng nhập

    # Lấy thông số trang từ query string (mặc định là trang 1)
    page = request.args.get('page', 1, type=int)
    
    # Lấy danh sách thành viên phân trang, 10 thành viên mỗi trang
    members = Member.query.paginate(page, per_page=10, error_out=False)

    # Truyền đối tượng phân trang vào template
    return render_template('admin_dashboard.html', members=members.items, pagination=members)

# Route đăng kí tài khoản thành viên mới
@admin_bp.route('/register_member', methods=['GET', 'POST'])
@login_required
def register_member():
    form = RegisterMemberForm()
    if form.validate_on_submit():
        member = Member(username=form.username.data,
                        fullname=form.fullname.data,
                        email=form.email.data)
        
        # Kiểm tra xem tên đăng nhập đã tồn tại chưa
        existing_member = Member.query.filter_by(username=form.username.data).first()
        if existing_member:
            flash('Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác.', 'danger')
            return redirect(url_for('admin.register_member'))
        
        # Kiểm tra xem email đã tồn tại chưa
        existing_email = Member.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email đã tồn tại. Vui lòng chọn email khác.', 'danger')
            return redirect(url_for('admin.register_member'))
        
        # Nếu không có lỗi, lưu thành viên mới vào cơ sở dữ liệu
        member.set_password(form.password.data)
        db.session.add(member)
        db.session.commit()
        flash('Tạo tài khoản thành viên thành công!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('register_member.html', form=form)

# Route hiển thị danh sách thành viên 
@admin_bp.route('/members')
@login_required
def members():
    members = Member.query.all()
    return render_template('members.html', members=members)

# Route xóa tài khoản thành viên
@admin_bp.route('/delete_member/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Xóa tài khoản thành viên thành công!', 'success')
    return redirect(url_for('admin.members'))

# Route chỉnh sửa thông tin thành viên
@admin_bp.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)
    form = RegisterMemberForm(obj=member)
    if form.validate_on_submit():
        member.fullname = form.fullname.data
        member.email = form.email.data
        if form.password.data:
            member.set_password(form.password.data)
        db.session.commit()
        flash('Cập nhật thông tin thành viên thành công!', 'success')
        return redirect(url_for('admin.members'))
    return render_template('edit_member.html', form=form, member=member)
