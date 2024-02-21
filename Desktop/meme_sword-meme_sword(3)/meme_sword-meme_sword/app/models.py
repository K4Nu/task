import os
from app import db,app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from app import login_manager
from datetime import datetime
from time import time
import jwt
from sqlalchemy import desc
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
    test_like=db.relationship("Vote_Like",backref="user",passive_deletes=True)
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

class File(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filename=db.Column(db.String(100),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey("post.id"),nullable=False)


class Comment(db.Model):
    _N = 2
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    path = db.Column(db.Text, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    replies = db.relationship("Comment", backref=db.backref("parent", remote_side=[id]),
                              lazy="dynamic")

    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + "." if self.parent else ""
        self.path = prefix + "{:0{}d}".format(self.id, self._N)
        db.session.commit()

    def level(self):
        return len(self.path)

class Post(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    desc=db.Column(db.String(1000))
    date=db.Column(db.DateTime,default=datetime.utcnow())
    user_id=db.Column(db.Integer(),db.ForeignKey("user.id"),nullable=False)
    file=db.relationship("File",backref="post",lazy=True)
    comment = db.relationship("Comment", backref="post", lazy=True, order_by="Comment.id.desc()")
    likes=db.relationship("Like",backref="post",passive_deletes=True)

class Vote_Like(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    type=db.Column(db.Enum('up','down'),nullable=False)
    author = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id"), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey("post.id"),nullable=False)

