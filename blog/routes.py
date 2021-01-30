import secrets
import os
from PIL import Image
from flask import render_template,url_for,flash,redirect,request
from blog import app,db,bcrypt
from blog.forms import Registration,LogIn,Account
from blog.models import User
from flask_login import login_user,current_user, logout_user,login_required





posts=[
    {
        'author':"Varun Sreedhar",
        'title':"Blog post 1",
        'content':"First Content",
        'date':"1st July"

    },

    {
        'author':"Sanjana Kumar",
        'title':"Blog post 2",
        'content':"Second Content",
        'date':"18th July"

    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',posts=posts)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=Registration()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LogIn()
    if form.validate_on_submit():
        
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash("Unsuccessfull please check your details","danger")
    return render_template('login.html',title='Log In',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_pic(form_pic):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_pic.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/profile_pic',picture_fn)

    output_size=(125,125)
    i=Image.open(form_pic)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn




@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form=Account()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_pic(form.picture.data)
            current_user.image_file=picture_file

        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Your account has been updates')
        return redirect(url_for('account'))

    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename='profile_pic/'+current_user.image_file)
    return render_template('account.html',title='Account',filename=image_file,form=form)
