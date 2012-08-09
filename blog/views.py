from blog import app
from models import Post
from decorators import login_required

from flask import render_template, flash, url_for, redirect
from flaskext import wtf
from flaskext.wtf import validators

from google.appengine.api import users
from google.appengine.ext import db

from jinja2 import Markup


class PostForm(wtf.Form):
    title = wtf.TextField('Title', validators=[validators.Required()])
    content = wtf.TextAreaField('Content', validators=[validators.Required()])


@app.route('/')
def redirect_to_home():
    return redirect(url_for('list_posts'))


@app.route('/posts')
def list_posts():
    posts = Post.all()
    return render_template('list_posts.html', posts=posts)


@app.route('/post/<string:key>/', methods=['GET', 'POST'])
def post(key):
    post = Post.get(key)
    return render_template('post.html', post=post)


@app.route('/modulo/<int:key>/', methods=['GET', 'POST'])
def post(key):
    
    return render_template('modulo.html', key=key)


@app.route('/<string:key>', methods=['GET', 'POST'])
def entrada(key):
    q = db.Query(Post)
    posts = q.filter('title =', key)
    if posts.count() == 0:
        return render_template('404.html', url=key)
    else:
        post = posts[0]
        return render_template('post.html', post=post)


@app.route('/posts/new', methods = ['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data,
                    content = Markup(form.content.data).unescape(),
                    author = users.get_current_user())
        post.put()
        flash('Entrada guardada en la base de datos.')
        return redirect(url_for('list_posts'))
    return render_template('new_post.html', form=form)



