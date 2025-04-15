from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User
from app.forms import RegisterMemberForm

# Khởi tạo blueprint cho admin
admin_bp = Blueprint('admin', __name__)

# Trang dashboard cho admin
# Chỉ admin mới có quyền truy cập trang này
@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này.', 'warning')
        return redirect(url_for('auth.login'))

    # Xử lý edit_id để xác định chỉnh sửa hay thêm mới
    edit_id = request.args.get('edit_id', type=int)
    member = None # Khởi tạo biến member để tránh lỗi khi không có edit_id

    # chỉnh sửa thành viên có /dashboard?edit_id= ...
    if edit_id:
        member = User.query.filter_by(id=edit_id).first_or_404()
        form = RegisterMemberForm(obj=member)
        form.id.data = member.id  # Gán ID vào hidden field
    else:
        form = RegisterMemberForm()

    # Khi ấn Submit thì gửi dữ liệu lên
    if form.validate_on_submit():
        if form.id.data:  # trường hợp 1: không có form.id.data
            member = User.query.filter_by(id=form.id.data).first_or_404()
            member.fullname = form.fullname.data
            member.email = form.email.data
            if form.password.data: # trường hợp 2: có form.password.data
                member.set_password(form.password.data)
            db.session.commit()
            flash('Cập nhật thành viên thành công!', 'success')
        else: 
            if User.query.filter_by(username=form.username.data).first():
                flash('Tên đăng nhập đã tồn tại.', 'danger')
                return redirect(url_for('admin.dashboard'))
            if User.query.filter_by(email=form.email.data).first():
                flash('Email đã tồn tại.', 'danger')
                return redirect(url_for('admin.dashboard'))

            # Tạo mới lại thành viên
            new_member = User(
                username=form.username.data,
                fullname=form.fullname.data,
                email=form.email.data,
                role='member' 
            )
            new_member.set_password(form.password.data)
            db.session.add(new_member)
            db.session.commit()
            flash('Tạo thành viên mới thành công!', 'success')

        return redirect(url_for('admin.dashboard'))

    # Lấy danh sách user và member
    page = request.args.get('page', 1, type=int)
    # Flask-SQLAlchemy có hỗ trợ phân trang
    pagination = db.paginate(
        User.query.filter(User.role.in_(['user', 'member'])),
        page=page,
        per_page=10,
        error_out=False
    )
    members = pagination.items

    return render_template('admin/dashboard.html',
                           form=form,
                           members=members,
                           pagination=pagination,
                           edit_id=edit_id)


# Xóa thành viên
# Chỉ admin mới có quyền xóa thành viên
@admin_bp.route('/dashboard/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_member(user_id):
    if current_user.role != 'admin':
        flash('Bạn không có quyền.', 'warning')
        return redirect(url_for('admin.dashboard'))
    member = User.query.get_or_404(user_id)
    db.session.delete(member)
    db.session.commit()
    flash('Xóa thành viên thành công!', 'success')
    return redirect(url_for('admin.dashboard'))
