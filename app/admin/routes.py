from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Task
from app.forms import RegisterMemberForm, AssignTaskForm
from werkzeug.utils import secure_filename
import os

# Cho phép các định dạng file
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    # Form giao nhiệm vụ 
    assign_id = request.args.get('assign_id', type=int)
    assign_member = User.query.get(assign_id) if assign_id else None
    assign_form = AssignTaskForm()

    # Khi ấn nút submit 
    if form.validate_on_submit():
        if form.id.data:  # trường hợp 1: Có form.id.data
            member = User.query.filter_by(id=form.id.data).first_or_404()
            member.fullname = form.fullname.data
            member.email = form.email.data
            if form.password.data: # Kiểm tra form.password.data
                member.set_password(form.password.data)
            db.session.commit()
            flash('Cập nhật thành viên thành công!', 'success')
        else: 
            # trường hợp 2: Không có form.id.data
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

    # Xử lý giao nhiệm vụ
    if assign_form.validate_on_submit() and 'assign_submit' in request.form and assign_member:
        # Xử lý upload file
        file_data = request.files.get(assign_form.file.name)
        filename = None
        if file_data and allowed_file(file_data.filename):
            filename = secure_filename(file_data.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_data.save(os.path.join(upload_folder, filename))
        else:
            flash('Vui lòng chọn file hợp lệ (pdf, docx, png, jpg, zip)!', 'danger')
            return redirect(url_for('admin.dashboard', assign_id=assign_member.id))
        
        # Tạo task mới
        new_task = Task(
            title=assign_form.title.data,
            description=assign_form.description.data,
            deadline=assign_form.deadline.data,
            assigned_to=assign_member.id,
            file=filename
        )
        db.session.add(new_task)
        db.session.commit()
        flash(f'Giao nhiệm vụ cho {assign_member.username} thành công!', 'success')
        return redirect(url_for('admin.dashboard', page=request.args.get('page', 1)))
    
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

    # Trả về template dashboard.html
    return render_template('admin/dashboard.html',
                        form=form,
                        members=members,
                        pagination=pagination,
                        edit_id=edit_id,
                        assign_id=assign_id,
                        assign_member=assign_member,
                        assign_form=assign_form)


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

@admin_bp.route('/assign_task/<int:user_id>', methods=['GET', 'POST'])
@login_required
def assign_task(user_id):
    if current_user.role != 'admin':
        flash('Không có quyền.', 'danger')
        return redirect(url_for('admin.dashboard'))

    form = AssignTaskForm()
    if form.validate_on_submit():
        filename = None
        file_data = request.files.get('file')
        if file_data and allowed_file(file_data.filename):
            filename = secure_filename(file_data.filename)
            file_data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            assigned_to=user_id,
            file=filename
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Giao nhiệm vụ thành công!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/assign_task.html', form=form, user_id=user_id)
