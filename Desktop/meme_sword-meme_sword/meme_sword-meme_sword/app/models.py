import os
from app import db,app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from app import login_manager
from datetime import datetime
from time import time
import jwt
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(60),unique=True,nullable=False)
    email=db.Column(db.String(60),unique=True,nullable=False)
    avatar=db.Column(db.String(60),default="default.jpg")
    password_hash=db.Column(db.String(60),nullable=False)
    post=db.relationship("Post",backref="author",lazy=True)
    comment=db.relationship("Comment",backref='author',lazy=True)
    likes=db.relationship("Like",backref="user",passive_deletes=True)
    def __repr__(self):
        return f'{self.username}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self,expires_in=600):
        return jwt.encode({"reset_password":self.id,"exp":time()+expires_in},
                           app.config["SECRET_KEY"],algorithm="HS256")

    @staticmethod
    def verify_reset_token(token):
        try:
            id=jwt.decode(token,app.config["SECRET_KEY"],algorithms=["HS256"])["reset_password"]
        except:
            return
        return User.query.get(id)
class Post(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    desc=db.Column(db.String(1000))
    date=db.Column(db.DateTime,default=datetime.utcnow())
    user_id=db.Column(db.Integer(),db.ForeignKey("user.id"),nullable=False)
    file=db.relationship("File",backref="post",lazy=True)
    comment=db.relationship("Comment",backref="post",lazy=True)
    likes=db.relationship("Like",backref="post",passive_deletes=True)

class File(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filename=db.Column(db.String(100),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey("post.id"),nullable=False)

class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    text=db.Column(db.String(200),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey("post.id"),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey("post.id"),nullable=False)