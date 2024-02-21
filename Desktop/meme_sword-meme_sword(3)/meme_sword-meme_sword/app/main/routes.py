from flask import Blueprint,request,render_template,send_from_directory
from app import app
from app.models import Post
from . import main


@main.route('/')
def index():
    page=request.args.get("page",1,type=int)
    per_page=3
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page,per_page=per_page)
    return render_template("index.html", posts=posts,per_page=per_page)

@main.route("/upload/<filename>")
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)