from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    date = db.Column(db.DateTime)

    def __init__(self, title, body, date = None):
        self.title = title
        self.body = body
        if date is None:
            date = datetime.utcnow()
        self.date = date

#temp redirect
@app.route('/')
def main():
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def index():

    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('post.html', title="Post", blog=blog)

    else:
        blogs = Blog.query.order_by(Blog.date.desc()).all()
        return render_template('main.html', title='Main Page', blogs = blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def delete_task():

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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog')

    return render_template('newpost.html', title = 'Add a Blog Entry')

if __name__ == '__main__':
    app.run()