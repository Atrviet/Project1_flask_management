from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, json, send_from_directory, abort, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from datetime import datetime, timedelta

from app.models import Task, Member, db, TaskLog
from app.forms import UpdateTaskForm, UploadReportForm, TaskLogForm
from app.extensions import mail, scheduler, socketio
from flask_wtf.csrf import generate_csrf

# Cập nhật task
from datetime import date
from app.models import Task, Progress
from app.forms import UpdateTaskForm, TaskProgressForm


member_bp = Blueprint('member', __name__, url_prefix='/member')

# Phần dowload file role admin gửi
@member_bp.route('/download/<filename>')
@login_required
def download_file(filename):
    # chỉ cho phép download nếu task thực sự thuộc về user hiện tại
    task = Task.query.filter_by(assignee_id=current_user.id, file=filename).first()
    if not task:
        abort(404)

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    return send_from_directory(
        directory=upload_folder,
        path=filename,
        as_attachment=True  # header để trình duyệt download
    )

# Trang dashboard cho member
@member_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'member':
        flash("Bạn không có quyền truy cập!", 'danger')
        return redirect(url_for('auth.login'))

    tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    return render_template('member/dashboard.html', tasks=tasks, csrf_token=generate_csrf())

# Cập nhật task
@member_bp.route('/task/<int:task_id>/update', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.assignee_id != current_user.id:
        flash("Bạn không có quyền chỉnh sửa task này.", 'danger')
        return redirect(url_for('member.dashboard'))

    task_form = UpdateTaskForm(obj=task)
    progress_form = TaskProgressForm()

    if request.method == 'POST' and task_form.validate() and progress_form.validate():
        # Cập nhật trạng thái & % hoàn thành
        task.status = task_form.status.data
        task.progress = task_form.progress.data
        db.session.commit()

        # Lưu tiến độ mới
        new_prog = Progress(
            task_id=task.id,
            user_id=current_user.id,
            description=progress_form.description.data
        )
        db.session.add(new_prog)
        db.session.commit()

        # Phát sự kiện realtime qua SocketIO
        socketio.emit('task_updated', {
            'task_id': task.id,
            'status': task.status,
            'progress': task.progress
        }, room=f'user_{current_user.id}')

        flash("Đã lưu trạng thái và tiến độ hôm nay!", 'success')
        return redirect(url_for('member.update_task', task_id=task.id))
    
    entries = Progress.query.filter_by(task_id=task.id, user_id=current_user.id).order_by(Progress.date.desc()).all()
    return render_template(
        'member/update_task.html',
        task=task,
        task_form=task_form,
        progress_form=progress_form,
        entries=entries
    )
    
# Xoá task
@member_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.assignee_id != current_user.id:
        flash("Bạn không thể xoá task không thuộc về mình.", 'danger')
        return redirect(url_for('member.dashboard'))

    db.session.delete(task)
    db.session.commit()
    flash("Xoá task thành công!", 'success')
    return redirect(url_for('member.dashboard'))


# Tải lên báo cáo
@member_bp.route('/upload_report', methods=['GET', 'POST'])
@login_required
def upload_report():
    form = UploadReportForm()
    if form.validate_on_submit():
        file = form.report.data
        filename = f"{current_user.username}_report_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        filepath = f"uploads/{filename}"
        file.save(filepath)
        flash("Tải file báo cáo thành công!", 'success')
        return redirect(url_for('member.dashboard'))

    return render_template('member/upload_report.html', form=form)

# Biều đồ tiến độ
@member_bp.route('/progress_chart')
@login_required
def progress_chart():
    tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    labels = [t.title for t in tasks]
    data = [t.progress for t in tasks]
    return render_template('member/progress_chart.html', labels=labels, data=data)

# API trả về tiến độ tổng
@member_bp.route('/api/progress')
@login_required
def api_progress():
    # Trả về tiến độ tổng hoặc task đầu
    tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    overall = sum(t.progress for t in tasks) / len(tasks) if tasks else 0
    return jsonify({'overall_progress': overall})

# Đăng ký job nhắc deadline
@scheduler.task('interval', id='deadline_reminder', hours=6)
def send_deadline_reminders():
    now = datetime.utcnow()
    upcoming = Task.query.filter(
        Task.due_date <= now + timedelta(days=1),
        Task.status != 'Completed'
    ).all()
    for task in upcoming:
        user = Member.query.get(task.assignee_id)
        if user and user.email:
            msg = Message(
                "Nhắc nhở deadline công việc",
                recipients=[user.email],
                body=f"Xin chào {user.username},\nTask '{task.title}' sắp đến hạn vào {task.due_date}. Vui lòng cập nhật tiến độ."
            )
            # Gửi email nhắc nhở
            mail.send(msg)


# Sự kiện realtime qua Socket.IO
@socketio.on('join')
def on_join(data):
    room = f"user_{current_user.id}"
    socketio.join_room(room)

@socketio.on('leave')
def on_leave(data):
    room = f"user_{current_user.id}"
    socketio.leave_room(room)
