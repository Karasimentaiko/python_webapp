from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, LoginManager, login_user, logout_user ,login_required
from flask_bootstrap import Bootstrap

from werkzeug.security import generate_password_hash, check_password_hash
import os

import sqlite3
import pytz

#ターミナル
#set FLASK_APP=hello
#set FLASK_ENV=development
#python -m flask run

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'os.urandom(24)'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(12))

@login_manager.user_loader
def loag_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def main():
    return render_template('main.html')


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        
        post =  Post(title=title, body=body)
        db.session.add(post)
        db.session.commit()
        return redirect('/index')
    
    else:
        return render_template('create.html')

@app.route('/sigup', methods=['GET', 'POST'])
def sigup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user =  User(username=username, password=generate_password_hash(password, method='sha256'))
        
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    
    else:
        return render_template('sigup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        #ユーザー名がデータベースに存在するか？
        if User.query.filter_by(username=username).first():
            user =  User.query.filter_by(username=username).first()
            #パスワード認証
            if check_password_hash( user.password, password):
                login_user(user)
                return redirect('/index')
            else:
                #パスワードが違った場合
                return redirect('/login')
                
        else:
            #データベースになければ新規作成画面にリダイレクト
            return redirect('/sigup')
        
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    
    if request.method == 'GET':
        return render_template('update.html', post=post)
    
    else:
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        
        db.session.commit()
        return redirect('/index')

@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    post = Post.query.get(id)
    
    db.session.delete(post)
    db.session.commit()
    return redirect('/index')