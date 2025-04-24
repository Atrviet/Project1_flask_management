from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db, socketio
from app.models import User, Task
from app.forms import RegisterMemberForm, AssignTaskForm
from werkzeug.utils import secure_filename
import os

# Task
from app.models import Progress, ProgressFeedback
from app.forms import FeedbackForm

# Email
from flask_mail import Message
from app.__init__ import db, mail
from app.models import Task, User

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

    # Lấy tất cả bản ghi tiến độ để hiển thị chung
    progress_entries_all = Progress.query.order_by(Progress.date.desc()).all()

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
    
    print(f" Method: {request.method}", flush=True)
    print(f" Errors: {assign_form.errors}", flush=True)
    print("assign_member:", assign_member, flush=True)
    print("form.data:", assign_form.data, flush=True)
    print("submit data:", request.form.get('submit'), flush=True)
    
    # Xử lý giao nhiệm vụ (lưu file lên disk, ghi filename, real‑time, console log)
    if assign_form.validate_on_submit() and assign_member:
        print("Form hợp lệ, bắt đầu xử lý...", flush=True)
        page = request.args.get('page', 1, type=int)

        # 1) Lấy file từ form
        upload = request.files.get(assign_form.file.name)
        if not upload or not allowed_file(upload.filename):
            flash('Vui lòng chọn file hợp lệ (pdf, docx, png, jpg, zip)!', 'danger')
            print(f"[ERROR] User {current_user.username} tải lên file không hợp lệ: {upload.filename if upload else 'no file'}")
            return redirect(url_for('admin.dashboard', assign_id=assign_member.id, page=page))

        # 2) Chuẩn hóa tên
        filename = secure_filename(upload.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        try:
            # 3 Lấy file từ form
            upload = request.files.get(assign_form.file.name)
            if not upload:
                print("❌ Không có file nào được gửi.")
            else:
                print(f"Đã nhận file: {upload.filename}")
                
            if not upload or not allowed_file(upload.filename):
                flash('Vui lòng chọn file hợp lệ (pdf, docx, png, jpg, zip)!', 'danger')
                print("❌ File không hợp lệ.")
                return redirect(url_for('admin.dashboard', assign_id=assign_member.id, page=page))

            # 2 Chuẩn hóa tên và đọc nội dung
            filename = secure_filename(upload.filename)
            file_bytes = upload.read()
            print(f"File '{filename}' đã được đọc với dung lượng {len(file_bytes)} bytes")

            # 3 Tạo Task mới
            new_task = Task(
                title=assign_form.title.data,
                description=assign_form.description.data,
                due_date=assign_form.deadline.data,
                assignee_id=assign_member.id,
                file=filename,
                file_data=file_bytes # file nhị phân
            )
            db.session.add(new_task)
            db.session.commit()
            print(f"Nhiệm vụ '{new_task.title}' đã được lưu vào DB (ID: {new_task.id})")

            # Emit socket
            socketio.emit('new_task', {
                'task_id': new_task.id,
                'title': new_task.title,
                'file_name': filename,
                'downloadUrl': url_for('member.download_file', task_id=new_task.id)
            }, room=f'user_{assign_member.id}')
            print("Đã phát sự kiện new_task qua socket")

            flash(f'Giao nhiệm vụ cho {assign_member.username} thành công!', 'success')
            return redirect(url_for('admin.dashboard', page=page))

        except Exception as e:
            print("❌ Lỗi khi xử lý upload:", str(e))
            flash("Có lỗi khi xử lý nhiệm vụ!", "danger")
            return redirect(url_for('admin.dashboard', assign_id=assign_member.id, page=page))

    
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
                        assign_form=assign_form,
                        progress_entries_all=progress_entries_all
                        )


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

# Giao nhiệm vụ cho từng thành viên
@admin_bp.route('/assign_task/<int:user_id>', methods=['GET', 'POST'])
@login_required
def assign_task(user_id):
    if current_user.role != 'admin':
        flash('Không có quyền.', 'danger')
        return redirect(url_for('admin.dashboard'))
    # In log để debug
    print(f"[assign_task] Method: {request.method}", flush=True)

    
    form = AssignTaskForm()
    print("TYPE OF deadline:", type(form.deadline).__name__, flush=True)
    print("AssignTaskForm loaded from:", AssignTaskForm.__module__, flush=True)
    if request.method == "POST":
        print("------ DEBUG deadline ------", flush=True)
        print("request.form:", request.form.to_dict(), flush=True)
        print("deadline raw:", request.form.get('deadline'), flush=True)
        form_valid = form.validate_on_submit()
        print("form_valid:", form_valid, "errors:", form.errors, flush=True)
        
    # Phần xử lý khi người dùng gửi form    
    if form.validate_on_submit():
        filename = None
        f = form.file.data
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.deadline.data, 
            assignee_id=user_id,            
            file=filename
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        # Gửi email thông báo
        user = User.query.get(user_id)
        if user and user.email:
            msg = Message(
                subject='Bạn được giao một nhiệm vụ mới',
                recipients=[user.email],
            )
            msg.body = (
                f"Chào {user.fullname},\n\n"
                f"Bạn vừa được giao nhiệm vụ mới:\n"
                f"• Tiêu đề: {new_task.title}\n"
                f"• Mô tả: {new_task.description}\n"
                f"• Hạn hoàn thành: {new_task.due_date.strftime('%d/%m/%Y %H:%M')}\n\n"
                "Vui lòng kiểm tra và thực hiện đúng hạn.\n\n"
                "—\nFrom Flask Team Management\n"
            )
            try:    
                mail.send(msg)
                flash('Giao nhiệm vụ thành công và đã gửi email nhắc nhở!', 'success')
            except Exception as e:
                # Nếu gửi thất bại, vẫn để task được tạo, nhưng báo lỗi
                current_app.logger.error(f"Error sending email: {e}")
                flash('Giao nhiệm vụ thành công nhưng gửi email thất bại.', 'warning')
        else:
            flash('Giao nhiệm vụ thành công nhưng không có email người dùng.', 'warning')
            
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/assign_task.html', form=form, user_id=user_id)

# Xoá Progress
@admin_bp.route('/delete_progress/<int:progress_id>', methods=['POST'])
@login_required
def delete_progress(progress_id):
    if current_user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này.', 'warning')
        return redirect(url_for('auth.login'))

    progress = Progress.query.get_or_404(progress_id)

    try:
        # Xóa tiến độ
        db.session.delete(progress)
        db.session.commit()
        flash('Xóa bản ghi tiến độ thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra khi xóa tiến độ: {str(e)}', 'danger')

    return redirect(url_for('admin.dashboard'))
