from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


# FORMS

class SearchForm(FlaskForm):
    searched_for = StringField("Searched", validators=[DataRequired()])
    search = SubmitField("Search")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # author = StringField("Author")
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


class NamerForm(FlaskForm):
    name = StringField("What's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    user_name = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    fv_color = StringField("Fav Color")
    pass_hash = PasswordField("Password",
                              validators=[DataRequired(), EqualTo('pass_hash2', message='Password Must Match')])
    pass_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Login')
