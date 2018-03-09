from flask import render_template,redirect,url_for,request
from . import auth
from flask import flash
from flask_login import logout_user,login_required,login_user,current_user
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,PasswordResetForm,PasswordResetRequestForm,ChangeEmailForm
from app.models import User
from app import db
from app.email import send_mail

@auth.before_app_request
def before_request():
    if  current_user.is_authenticated :
        current_user.ping()
        if  not current_user.confirmed \
        and request.endpoint[:5] != 'auth.' \
        and request.endpoint != 'static'  :
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() :
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remenber_me.data)
            return redirect( url_for('main.index'))
        flash('你的密码或者邮箱地址错误')
    return render_template('/auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经登出了账户')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email,'确认邮件','auth/email/confirm',token=token,user=user)
        flash('请到邮箱确认你的邮件')
        return redirect(url_for('auth.login'))
    return render_template('/auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed :
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('确认完成')
    else :
        flash('无法完成确认')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed :
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_mail(current_user.email, '确认邮件', 'auth/email/confirm', token=token, user=current_user)
    return redirect(url_for('main.index'))

@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('修改成功')
        else :
            flash('修改失败')
        return redirect(url_for('main.index'))
    return render_template('auth/change_password.html',form=form)

@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user :
            token = user.generate_reset_token()
            send_mail(user.email,'重置密码','auth/email/reset_password',token=token,user=user)
            flash('请到邮箱确认邮件')
        else :
            flash('这个用户不存在')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
    form = PasswordResetForm()
    if form.validate_on_submit() :
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('用户不存在')
        if user.reset_password(token,form.password.data) :
            flash('密码修改成功')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)

@auth.route('/change-email',methods=['GET','POST'])
@login_required
def change_email_request() :
    form = ChangeEmailForm()
    if form.validate_on_submit() :
        if current_user.verify_password(form.password.data) :
            new_email = form.email.data
            token = current_user.generate_change_email_token(new_email)
            send_mail(new_email,'重置邮箱','auth/email/change_email',token=token,user=current_user)
            flash('请到新的邮箱地址确认你的邮件')
            return redirect(url_for('main.index'))
        else :
            flash('密码或邮箱地址不正确')
    return render_template('auth/change_email.html',form=form)

@auth.route('/change-email/<token>',methods=['GET','POST'])
@login_required
def change_email(token) :
    if current_user.change_email(token) :
        flash('修改成功')
    else :
        flash('修改失败')
    return redirect(url_for('main.index'))
















