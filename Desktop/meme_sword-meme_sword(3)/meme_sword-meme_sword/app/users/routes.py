from flask import Blueprint,render_template,url_for,redirect,abort,request,flash
import os
from .forms import RegisterForm,LoginForm,ResetPassword,ResetEmail
from werkzeug.utils import secure_filename
from app import app,db
from app.models import User,Post
from flask_login import current_user,logout_user,login_user,login_required
from .utils import  send_password_reset_email
from . import users

@users.route("/register",methods=["GET","POST"])
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
        return redirect(url_for('users.login'))
    return render_template("register.html",title="Register",form=form)

@users.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
    return render_template("login.html",title="Login",form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@login_required
@users.route("/account")
def account():
    page=request.args.get("page",1,type=int)
    per_page=5
    posts=Post.query.order_by(Post.id.desc()).filter_by(author=current_user).paginate(page=page,per_page=per_page)
    return render_template("account.html",posts=posts,title="Account",per_page=per_page)

@users.route("/reset_password/request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for('main.index'))

    form = ResetEmail()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash("Password reset email has been sent.")
            return redirect(url_for('main.index'))
        else:
            flash("No user found with this email.")

    return render_template('email.html', form=form, title="Reset Password")

@users.route("/reset_password/<token>",methods=["GET","POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user=User.verify_reset_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form=ResetPassword()
    if form.validate_on_submit():
        user.set_password(form.p1.data)
        db.session.commit()
        return redirect(url_for('users.login'))
    return render_template("reset_password.html",form=form)