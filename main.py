from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'password'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, date = None):
        self.title = title
        self.body = body
        self.owner = owner
        if date is None:
            date = datetime.utcnow()
        self.date = date

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash('You must login before posting.', 'message')
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', title='User Index', users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html', title = 'Login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and len(password) > 3 and len(username) > 3 and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            if existing_user:
                flash('username is taken', 'error')
            if len(username) < 4:
                flash('username must be more than 3 characters', 'error')
            if len(password) < 4:
                flash('password must be more than 3 characters', 'error')
            if password != verify:
                flash("passwords don't match", 'error')

    return render_template('signup.html', title = 'Sign Up', username=username)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def list_blogs():

    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('post.html', title="Post", blog=blog)
    user_id = request.args.get('user')
    if user_id:
        blogs = Blog.query.filter_by(owner_id=user_id).order_by(Blog.date.desc()).all()
        user = User.query.filter_by(id=user_id).first()
        return render_template('singleUser.html', title=user.username+"'s Posts", blogs=blogs)    
    else:
        users = User.query.all()
        blogs = Blog.query.order_by(Blog.date.desc()).all()
        return render_template('main.html', title='Main Page', blogs = blogs, users = users)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_title_error = False
        blog_body_error = False
        if not blog_title or not blog_body:  
            if not blog_title:
                blog_title_error = True
            if not blog_body:
                blog_body_error = True
            return render_template('newpost.html',  title = 'Add a Blog Entry', blog_title = blog_title, blog_body = blog_body, blog_title_error = blog_title_error, blog_body_error = blog_body_error)
        else:
            user = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title, blog_body, user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')

    return render_template('newpost.html', title = 'Add a Blog Entry')

if __name__ == '__main__':
    app.run()