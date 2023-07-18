# to run this code, create a file named private_var and declare there:
# secret_key
# email
# app password for your email
# Happy Birthday 😊
from email.message import EmailMessage
from flask import Flask, render_template, redirect, request, url_for, flash,abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import registerForm,loginForm,make_wishForm
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from twisted.internet import task, reactor
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime as dt
import smtplib
from private_var import *
Base = declarative_base()
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRETE_KEY
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///birthdays.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

##CONFIGURE TABLES
class User(db.Model,UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(250),nullable=False)
    password=db.Column(db.String(250),nullable=False)
    email=db.Column(db.String(250),nullable=False)
    friends=relationship('Friend',back_populates='wisher')

class Friend(db.Model):
    __tablename__='friends'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    birthDate=db.Column(db.Date(),nullable=False)
    wish=db.Column(db.Text,nullable=False)
    email=db.Column(db.String(250),nullable=False)
    wisher_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    wisher=relationship('User',back_populates='friends')

# db.create_all()
ckeditor = CKEditor(app)
Bootstrap(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/show_wish/<int:wish_id>")
def show_wish(wish_id,):
    return render_template('wish.html',wish=Friend.query.get(wish_id),logged_in=current_user.is_authenticated)

@app.route("/")
def home():
    return render_template('index.html',all_posts={},logged_in=current_user.is_authenticated)

# REGISTER
@app.route("/register",methods=['GET','POST'])
def register():
    form=registerForm()
    if form.validate_on_submit():
        user=User(name=form.name.data,email=form.email.data,password=generate_password_hash(password=form.password.data,method='pbkdf2:sha256',salt_length=8))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('all_wishes'))
    return render_template("register.html",form=form,logged_in=current_user.is_authenticated)

# LOGIN
@app.route("/login", methods=['GET','POST'])
def login():
    form=loginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        user=User.query.filter_by(email=email).first()
        if user is None:
            flash('That email does not exist, please try again')
        else:
            is_correct_password=check_password_hash(user.password,password)
            if is_correct_password:
                login_user(user)
                return redirect(url_for('all_wishes'))
            flash('Passwod incorrect, please try again')
    return render_template("login.html",form=form,logged_in=current_user.is_authenticated)
@app.route('/delete_wish/<int:wish_id>')
def delete_wish(wish_id):
    friend=Friend.query.get(wish_id)
    db.session.delete(friend)
    db.session.commit()
    return redirect(url_for('all_wishes'))
@app.route('/contact')
def contact():
    return render_template('contact.html',logged_in=current_user.is_authenticated)
@app.route('/make_wish',methods=['GET','POST'])
def make_wish():
    form=make_wishForm()
    if form.validate_on_submit():
        friend=Friend(birthDate=form.birthDate.data,name=form.name.data,wish=form.wish.data,email=form.email.data,wisher_id=current_user.id)
        db.session.add(friend)
        db.session.commit()
        return redirect(url_for('all_wishes'))
    return render_template('make-wish.html',form=form,is_edit=False,logged_in=current_user.is_authenticated)
@app.route("/edit-wish/<int:wish_id>",methods=['GET', 'POST'])
def edit_wish(wish_id):
    friend=Friend.query.get(wish_id)
    form=make_wishForm(name=friend.name,birthDate=friend.birthDate,email=friend.email,wish=friend.wish)
    if form.validate_on_submit():
        friend.name=form.name.data
        friend.birthDate=form.birthDate.data
        friend.email=form.email.data
        friend.wish=form.wish.data
        db.session.commit()
        return redirect(url_for('show_wish',wish_id=wish_id))
    return render_template('make-wish.html',form=form,is_edit=True,logged_in=current_user.is_authenticated)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
@app.route('/all_wishes')
def all_wishes():
    if current_user==None:
        return redirect(url_for('login'))
    return render_template('wishes.html',wishes=Friend.query.filter_by(wisher_id=current_user.id),logged_in=current_user.is_authenticated)
def sensor():
    my_email=EMAIL
    password=PASSWORD
    today=dt.now()
    friends=db.session.query(Friend).all()
    for friend in friends:
        if f"{friend.birthDate}"[5:]==f"{today.strftime('%m')}-{today.strftime('%d')}":
            age=today.year-int(f"{friend.birthDate}"[:4])
            msg = EmailMessage()
            msg['Subject'] = f"congrats for turning {age}"
            msg['From'] = my_email 
            msg['To'] = f"{friend.email}"
            # create a nice email massage
            msg.set_content(f'''
            <!DOCTYPE html>
            <html>
                <body style="background-color:#eee;padding:10px 20px;">
                    <div >
                        <h2 style="font-family:Georgia, 'Times New Roman', Times, serif;color#454349;">congrats for turning {age}</h2>
                    </div>
                    <div style="padding:20px 0px">
                        <div style="height: 500px;width:400px">
                            {friend.wish}
                            </div>
                        </div>
                    </div>
                </body>
            </html>
            ''', subtype='html')
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(my_email, password=password) 
                smtp.send_message(msg)
        

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'interval',days=1,max_instances=2)
sched.start()
if __name__=='__main__':
    app.run(debug=True)

