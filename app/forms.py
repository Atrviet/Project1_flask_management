from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, BooleanField, TextAreaField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from app.extensions import db, login_manager
from flask_wtf.file import FileField, FileAllowed, FileRequired

# Form cho trang đăng nhập use, admin
class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    captcha  = StringField('Mã xác nhận', validators=[DataRequired()])
    remember_me = BooleanField('Ghi nhớ đăng nhập') 
    submit = SubmitField('Đăng nhập')

# Form Giao nhiệm vụ role admin
class AssignTaskForm(FlaskForm):
    id = HiddenField()
    title = StringField('Tiêu đề', validators=[DataRequired()])
    description = TextAreaField('Mô tả')
    file = FileField('Tệp đính kèm')
    deadline = DateTimeField('Deadline (YYYY-MM-DD HH:MM:SS)', format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Giao nhiệm vụ')
    
# Form cho trang đăng ký thành viên mới
class RegisterMemberForm(FlaskForm):
    id = HiddenField()  # để phân biệt tạo mới hay chỉnh sửa
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    fullname = StringField('Họ tên', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')
    
# 
class UpdateTaskForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired()])
    description = TextAreaField('Mô tả')
    deadline = DateTimeField('Hạn chót', format='%Y-%m-%d %H:%M:%S')
    progress = IntegerField('Tiến độ (%)', validators=[NumberRange(min=0, max=100)])
    submit = SubmitField('Cập nhật')
    

class UploadReportForm(FlaskForm):
    report = FileField('Báo cáo', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Chỉ cho phép file PDF/DOC/DOCX!')
    ])
    submit = SubmitField('Tải lên')