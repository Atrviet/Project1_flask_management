from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, BooleanField, TextAreaField, DateTimeField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange
from app.extensions import db, login_manager
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields import DateField



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
    deadline = DateField(
        'Deadline',
        format='%Y-%m-%d',
        render_kw={'type': 'date'},
        validators=[DataRequired(message="Vui lòng chọn ngày hợp lệ.")]
    )
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
    
# Form cho việc cập nhật tiến độ
class UpdateTaskForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired()])
    description = TextAreaField('Mô tả')
    deadline = DateTimeField('Hạn chót', format='%Y-%m-%d %H:%M:%S')
    progress = IntegerField('Tiến độ (%)', validators=[NumberRange(min=0, max=100)])
    submit = SubmitField('Cập nhật')
    
# Form cho việc tải lên báo cáo
class UploadReportForm(FlaskForm):
    report = FileField('Báo cáo', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx'], 'Chỉ cho phép file PDF/DOC/DOCX!')
    ])
    submit = SubmitField('Tải lên')

# From cho cập nhật task từ member
class UpdateTaskForm(FlaskForm):
    status = SelectField(
        'Trạng thái',
        choices=[
            ('New', 'Mới'),
            ('In Progress', 'Đang làm'),
            ('Completed', 'Hoàn thành')
        ],
        validators=[DataRequired()]
    )
    progress = IntegerField(
        'Tiến độ (%)',
        validators=[DataRequired(), NumberRange(min=0, max=100)]
    )
    submit = SubmitField('Lưu')
    
# form upload tiến độ công việc trong ngày
class TaskLogForm(FlaskForm):
    description = TextAreaField('Công việc đã làm hôm nay', validators=[DataRequired()])
    progress = IntegerField('Tiến độ (%)', validators=[DataRequired()])
    submit = SubmitField('Gửi báo cáo')

# Form cho việc cập nhật tiến độ
class TaskProgressForm(FlaskForm):
    description = TextAreaField('Mô tả tiến độ hôm nay', validators=[DataRequired()])
    submit = SubmitField('Lưu tiến độ')

# Form cho việc gửi nhận xét từ admin
class FeedbackForm(FlaskForm):
    comment = TextAreaField('Nhận xét của Admin', validators=[DataRequired()])
    submit = SubmitField('Gửi nhận xét')