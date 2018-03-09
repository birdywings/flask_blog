from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm,CommentForm
from .. import db
from ..models import User,Role,Permission,Post,Comment
from flask import render_template,current_app,redirect,url_for,session,abort,flash,request,make_response
from ..email import send_mail
from datetime import datetime
from flask_login import  login_required,current_user
from ..decorators import admin_required,permission_required

@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed :
        query = current_user.followed_posts
    else :
        query = Post.query
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page)
    posts = pagination.items
    return render_template('index.html',current_time=datetime.utcnow(),form=form,posts=posts,pagination=pagination,
                           show_followed=show_followed)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit() :
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('已更新你的信息')
        return  redirect(url_for('main.user',username=current_user.name))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit() :
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('已更新用户信息')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form,user=user)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post= Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment  = Comment(body=form.body.data,post=post,author=current_user._get_current_object())
        db.session.add(comment)
        flash('你的评论已经提交')
        return redirect(url_for('.post',id=post.id))
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page,5) # asc()是顺序，desc()是倒叙
    comments = pagination.items
    return render_template('post.html',posts=[post],form=form,comments=comments,pagination=pagination)

@main.route('/edit_post/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Post.query.get_or_404(id)

    if current_user != post.author and  not current_user.can(Permission.ADMINISTER):
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('已更新文章')
        return redirect(url_for('.edit_post',id = post.id))

    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None :
        flash('不存在用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('您已经关注了此用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('您关注了%s' % username)
    return redirect(url_for('.user',username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None :
        flash('不存在用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        current_user.unfollow(user)
        flash('您已不再关注%s' % username)
        return redirect(url_for('.user', username=username))



@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None :
        flash('不存在用户')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=1)
    pagination = user.followers.paginate(page)
    follows = [{'user':item.follower,'timestamp':item.timestamp}for item in pagination.items]
    return  render_template('followers.html',follows=follows,user=user,title='的粉丝',pagination=pagination
                            ,endpoint='.followers')

@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=1)
    pagination = user.followed.paginate(page)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', follows=follows, user=user, title='关注的人', pagination=pagination
                           , endpoint='.followers')

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, 5)  # asc()是顺序，desc()是倒叙
    comments = pagination.items
    return render_template('moderate.html', posts=[post],comments=comments, pagination=pagination)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate'))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate'))













