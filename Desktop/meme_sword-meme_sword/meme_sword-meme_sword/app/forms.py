from wtforms import StringField, PasswordField,SubmitField,FileField,TextAreaField,MultipleFileField
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.validators import DataRequired,Email,EqualTo
from werkzeug.utils import secure_filename
import os
from app.models import User

class Login(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

class RegisterForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    p1=PasswordField("Password",validators=[DataRequired()])
    p2=PasswordField("Password Repeat",[DataRequired(),EqualTo("p1")])
    email=StringField('Email',validators=[DataRequired(),Email()])
    image=FileField("img")
    submit=SubmitField("Submit")

    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken")

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already taken")

    def validate_file(self, image):
        size = 25 * 1024 * 1024
        if image.data:
            image.data.seek(0, 2)  # Move the file pointer to the end of the file
            file_size = image.data.tell()  # Get the current position (file size)
            image.data.seek(0)  # Move the file pointer back to the beginning

            if file_size > size:
                raise ValidationError("Image is too big!")

class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    desc=TextAreaField("Description")
    images=MultipleFileField("Images")
    submit=SubmitField("Submit")
    def validate_images(self, field):
        if len(field.data) > 3:
            raise ValidationError("Only 3 files are allowed")
class CommentForm(FlaskForm):
    text=TextAreaField("Comment this post",validators=[DataRequired()])
    submit=SubmitField("Submit")

class ResetPassword(FlaskForm):
    p1=PasswordField("Password",validators=[DataRequired()])
    p2=PasswordField("Repeat Password",validators=[DataRequired(),EqualTo("p1")])
    submit=SubmitField("Submit")

class ResetEmail(FlaskForm):
    email=StringField("Email",validators=[DataRequired(),Email()])
    submit=SubmitField("Submit")