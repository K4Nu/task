from flask import Blueprint,redirect,url_for,render_template,abort,request,flash
import os
from app import app
from flask_login import current_user,login_required
from app import db
from werkzeug.utils import secure_filename
from app.models import Post,File,Comment,Vote_Like,Like
from .forms import PostForm,CommentForm
from PIL import Image
from . import posts
@login_required
@posts.route("/create_post",methods=["GET","POST"])
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
        return redirect(url_for('main.index'))
    return render_template("create_post.html",title="Create Post",form=form)

@login_required
@posts.route("/delete_post/<int:id>",methods=["POST","GET"])
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
    return redirect(url_for('users.account',page=page))

@login_required
@posts.route("/update_post/<int:id>",methods=["GET","POST"])
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

@posts.route("/post/<id>", methods=["GET", "POST"])
def post(id):
    post = Post.query.filter_by(id=id).first()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(text=form.text.data, post_id=id, user_id=current_user.id)
        comment.save()
        return redirect(url_for('posts.post', id=id))
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.path).all()
    return render_template("post.html", post=post, form=form, title=post.title,comments=comments)

@login_required
@posts.route("/delete_comment/<id>")
def delete_comment(id):
    comment=Comment.query.filter_by(id=id).first()
    post=comment.post_id
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('posts.post',id=post))

@login_required
@posts.route("/like_post/<id>",methods=["POST","GET"])
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
    return redirect(url_for('main.index',page=page))

@login_required
@posts.route("/comment_vote/<int:comment_id>/<string:vote_type>")
def comment_vote(comment_id,vote_type):
    page=Comment.query.get(comment_id)
    if vote_type not in ["up", "down"]:
        flash("Invalid vote type","warning")
        return redirect(url_for('main.index'))
    comment=Comment.query.get(comment_id)
    if not comment:
        flash("Invalid comment!","warning")
        return redirect(url_for("main.index"))
    ex_vote=Vote_Like.query.filter_by(author=current_user.id,comment_id=comment_id).first()
    if ex_vote:
        if ex_vote.type==vote_type:
            db.session.delete(ex_vote)
        else:
            ex_vote.type=vote_type
    else:
        new_vote = Vote_Like(type=vote_type, author=current_user.id, comment_id=comment_id)
        db.session.add(new_vote)
    try:
        db.session.commit()
    except Exception as e:
        flash("Error updating your vote!", "danger")
    return redirect(url_for('posts.post',id=page.post_id))

@login_required
@posts.route("/reply/<int:id_comment>",methods=["POST","GET"])
def reply(id_comment):
    form=CommentForm()
    parent=Comment.query.get(id_comment)
    if not parent:
        abort(400)
    if form.validate_on_submit():
        new_comment=Comment(text=form.text.data,post_id=parent.post_id,user_id=current_user.id,parent_id=parent.id)
        new_comment.save()
    return redirect(url_for('posts.post',id=parent.post_id))
