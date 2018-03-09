from flask_wtf import FlaskForm         #引入基类
from wtforms import StringField,SubmitField,BooleanField,PasswordField,ValidationError #关于表单HTML标准字段
from wtforms.validators import DataRequired,Email,Length,Regexp,EqualTo #引入验证函数
from app.models import User

class LoginForm(FlaskForm):
    email =  StringField('Email',validators=[DataRequired(),Email(),Length(1,64)])
    password = PasswordField('Password',validators=[DataRequired()])
    remenber_me = BooleanField('记住我')
    submint = SubmitField('确定')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('Username',validators=[DataRequired(),Length(1,64),
                                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password  = PasswordField('Password',validators=[DataRequired(),EqualTo('password2'
                                                         ,message='输入的两次密码必须匹配')])
    password2 = PasswordField('再次输入Password',validators=[DataRequired()])
    submint = SubmitField('注册')

    def validate_email(self,filed):
        if User.query.filter_by(email=filed.data).first():
            raise ValidationError('这个邮箱地址已经注册')

    def validate_username(self,filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError('这个用户名已经注册')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('原密码',validators=[DataRequired()])
    password = PasswordField('新密码',validators=[DataRequired(),EqualTo('password2',message='输入的两次密码必须匹配')])
    password2 = PasswordField('再次输入新密码',validators=[DataRequired()])
    submint = SubmitField('确定')

class PasswordResetRequestForm(FlaskForm) :
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    submint = SubmitField('确定')

class PasswordResetForm(FlaskForm) :
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('新密码', validators=[DataRequired(), EqualTo('password2', message='输入的两次密码必须匹配')])
    password2 = PasswordField('再次输入新密码', validators=[DataRequired()])
    submint = SubmitField('确定')

    def validate_email(self,filed) :
        if not User.query.filter_by(email=filed.data).first() :
            raise ValidationError('邮箱不存在')

class ChangeEmailForm(FlaskForm):
    email = StringField('新Email', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('密码',validators=[DataRequired()])
    submint = SubmitField('确定')

    def validate_email(self,filed) :
        if  User.query.filter_by(email=filed.data).first() :
            raise ValidationError('邮箱已存在')
