from flask_wtf import FlaskForm         #引入基类
from wtforms import StringField,SubmitField,BooleanField,PasswordField,TextAreaField,SelectField,ValidationError #关于表单HTML标准字段
from wtforms.validators import DataRequired,Email,Length,Regexp #引入验证函数
from ..models import User,Role
from flask_pagedown.fields import PageDownField

class NameForm(FlaskForm): #这是一个名字表单
    name  = StringField('what is your name?',validators=[DataRequired()])
    submit= SubmitField('确定')

class EditProfileForm(FlaskForm) :
    name = StringField('名字', validators=[DataRequired(),Length(0,64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('确定')

class EditProfileAdminForm(FlaskForm) :
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64),Email()])
    username = StringField('用户名字', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('认证信息')
    role = SelectField('权限', coerce=int)
    name = StringField('名字', validators=[DataRequired(), Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('确定')

    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices = [(role.id,role.name)for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and User.query.filter_by(email = field.data).first() :
            raise ValidationError('这个邮箱已经注册')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username = field.data).first() :
            raise ValidationError('这个用户名已经注册')

class PostForm(FlaskForm) :
    body = PageDownField('有什么想说的?')
    submit = SubmitField('确定')

class CommentForm(FlaskForm):
    body = StringField('评论',validators=[DataRequired()])
    submit = SubmitField('确定')