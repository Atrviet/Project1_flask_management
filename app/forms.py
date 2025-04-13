from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from app.extensions import db, login_manager  # import db và login_manager từ extensions.py

# Form cho trang đăng nhập use, admin
class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')
    
# Form cho trang đăng ký thành viên mới
class RegisterMemberForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    fullname = StringField('Họ tên', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')