from wtforms import StringField, PasswordField,SubmitField,FileField,TextAreaField,MultipleFileField
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.validators import DataRequired
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