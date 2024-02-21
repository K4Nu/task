from app import app,db,mail
from flask import render_template,request,redirect,url_for,abort, send_from_directory,flash
from flask_login import current_user,logout_user,login_user,login_required
from app.models import User,Post,File,Comment,Like
from app.forms import LoginForm,RegisterForm,PostForm,CommentForm,ResetPassword,ResetEmail
from werkzeug.utils import secure_filename
import os
import logging
from flask_mail import Message
from app.functions import send_password_reset_email
from PIL import Image
import imageio

@app.route('/')
def index():
    page=request.args.get("page",1,type=int)
    per_page=3
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page,per_page=per_page)
    return render_template("index.html", posts=posts)

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.p1.data)
        file=form.image.data
        if file:
            _,extension=os.path.splitext(secure_filename(file.filename))
            filename=str(form.username.data)+extension
            if extension not in app.config["UPLOAD_EXTENSIONS"]:
                abort(400)
            file.save(os.path.join(app.static_folder,"imgs", filename))
            user.avatar=filename
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html",title="Register",form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    return render_template("login.html",title="Login",form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route("/create_post",methods=["GET","POST"])
def create_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,desc=form.desc.data,user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        files = form.images.data
        i=0
        for file in files:
            if file:
                size=600
                i+=1
                _, extension = os.path.splitext(secure_filename(file.filename))
                filename = str(post.id)+str(i)+ extension
                if extension not in app.config["UPLOAD_EXTENSIONS"]:
                    abort(400)
                if extension in [".gif",".mp4"]:
                    file.save(os.path.join(app.static_folder, "imgs", filename))
                    f=File(filename=filename,post_id=post.id)
                else:
                    img=Image.open(file)
                    width=size if img.width>size else img.width
                    img.thumbnail((width,img.height))
                    img.save(os.path.join(app.static_folder, "imgs", filename))
                    img.close()
                    f=File(filename=filename,post_id=post.id)
                db.session.add(f)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template("create_post.html",title="Create Post",form=form)


@login_required
@app.route("/account")
def account():
    page=request.args.get("page",1,type=int)
    per_page=5
    posts=Post.query.order_by(Post.id.desc()).filter_by(author=current_user).paginate(page=page,per_page=per_page)
    return render_template("account.html",posts=posts,title="Account",per_page=per_page)

@login_required
@app.route("/delete_post/<int:id>",methods=["POST","GET"])
def delete_post(id):
    page=request.args.get("page",default=1,type=int)
    post=Post.query.get_or_404(id)
    comms=Comment.query.filter_by(post_id=id).all()
    files=File.query.filter_by(post_id=id).all()
    for file in files:
        file_path=os.path.join(app.static_folder,"imgs",file.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(file)
    for comment in comms:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('account',page=page))

@login_required
@app.route("/update_post/<int:id>",methods=["GET","POST"])
def update_post(id):
    page = request.args.get("page", default=1, type=int)
    form=PostForm()
    post=Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        post.title=form.title.data
        post.desc=form.desc.data
        db.session.commit()
        return redirect(url_for('account',page=page))
    elif request.method=="GET":
        form.title.data=post.title
        form.desc.data=post.desc
    return render_template("create_post.html",form=form,title="Update")


@app.route("/upload/<filename>")
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route("/post/<id>",methods=["GET","POST"])
def post(id):
    post=Post.query.filter_by(id=id).first()
    form=CommentForm()
    if form.validate_on_submit():
        comment=Comment(text=form.text.data,post_id=id,user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post',id=id))
    return render_template("post.html",post=post,form=form,title=post.title)

@login_required
@app.route("/delete_comment/<id>")
def delete_comment(id):
    comment=Comment.query.filter_by(id=id).first()
    post=comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('post',id=post))


@app.route("/reset_password/request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for('index'))

    form = ResetEmail()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash("Password reset email has been sent.")
            return redirect(url_for('index'))
        else:
            flash("No user found with this email.")

    return render_template('email.html', form=form, title="Reset Password")

@app.route("/reset_password/<token>",methods=["GET","POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user=User.verify_reset_token(token)
    if not user:
        return redirect(url_for('index'))
    form=ResetPassword()
    if form.validate_on_submit():
        user.set_password(form.p1.data)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("reset_password.html",form=form)

@login_required
@app.route("/like-post/<id>",methods=["POST","GET"])
def like_post(id):
    page=request.args.get("page",default=1,type=int)
    post=Post.query.filter_by(id=id).first()
    like=Like.query.filter_by(author=current_user.id,post_id=post.id).first()
    if not post:
        abort(400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like=Like(author=current_user.id,post_id=post.id)
        db.session.add(like)
        db.session.commit()
    return redirect(url_for('index',page=page))