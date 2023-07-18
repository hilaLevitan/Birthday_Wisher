from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,DateField,DateTimeLocalField
from wtforms.validators import DataRequired, URL,Email,InputRequired
from flask_ckeditor import CKEditorField

class registerForm(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    email=StringField('Email',validators=[Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("SIGN ME UP!")

class loginForm(FlaskForm):
    email=StringField('email',validators=[Email()])
    password=PasswordField('password',validators=[DataRequired()])
    submit=SubmitField('Let Me In')
class make_wishForm(FlaskForm):
    name=StringField("Friend's name",validators=[DataRequired()])
    email=StringField("Friend's Email",validators=[Email()])
    birthDate = DateField('Birth Date', format='%Y-%m-%d')
    wish=CKEditorField('Birthday Wish',validators=[DataRequired()])
    submit=SubmitField('SUBMIT WISH')