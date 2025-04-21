from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

mail = Mail()

def send_deadline_reminders():
    upcoming_tasks = Task.query.filter(
        Task.due_date <= datetime.utcnow() + timedelta(days=1),
        Task.status != 'Hoàn thành'
    ).all()
    for task in upcoming_tasks:
        user = Member.query.get(task.assignee_id)
        if user:
            msg = Message("Nhắc nhở Deadline",
                          recipients=[user.email],
                          body=f"Task '{task.title}' sắp đến hạn vào {task.due_date}. Vui lòng kiểm tra lại tiến độ.")
            mail.send(msg)

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=send_deadline_reminders, trigger="interval", hours=6)
    scheduler.start()
