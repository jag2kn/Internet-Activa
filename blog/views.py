# -*- coding: utf-8 -*-
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

class PostDelForm(wtf.Form):
    title = wtf.HiddenField('Title', validators=[validators.Required()])
    content = wtf.HiddenField('Content', validators=[validators.Required()])


@app.route('/')
def redirect_to_home():
    return redirect('/modulo/1/')


@app.route('/<string:key>', methods=['GET', 'POST'])
def entrada(key):
    q = db.Query(Post)
    posts = q.filter('title =', key)
    if posts.count() == 0:
        return render_template('404.html', url=key)
    else:
        post = posts[0]
        return render_template('post.html', post=post)



@app.route('/posts')
def list_posts():
    posts = Post.all().order("-when")
    return render_template('list_posts.html', posts=posts)


@app.route('/post/<string:titulo>/', methods=['GET', 'POST'])
def post(titulo):
    q = db.Query(Post)
    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', url=titulo)
    else:
        post = posts[0]
        return render_template('post.html', post=post)
    return render_template('post.html', post=post)


@app.route('/modulo/<int:id>/', methods=['GET', 'POST'])
def modulo(id):
    titulo = "Titulo"
    descripcion = "Descripcion descripcion descripcion descripcion descripcion descripcion descripcion descripcion descripcion descripcion"
    mes = "Sep"
    dias  = "12/23"
    return render_template('modulo.html', numero=id, titulo=titulo, descripcion=descripcion, mes=mes, dias=dias)



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


@app.route('/posts/edit/<string:titulo>/', methods = ['GET', 'POST'])
@login_required
def edit_post(titulo):
    form = PostForm()
    q = db.Query(Post)
    if form.validate_on_submit():
        posts = q.filter('title =', titulo)
        if posts.count() == 0:
            return render_template('error.html', mensaje="No se encontró el post editado")
        else:
            post = posts[0]
            flash(post.key())
            db.delete(post.key())
            post1 = Post(title = form.title.data,
                    content = Markup(form.content.data).unescape(),
                    author = users.get_current_user())
            post1.put()
            flash('Entrada actualizada en la base de datos.')
            return render_template('error.html', mensaje="Post editado")
            #return redirect(url_for('list_posts'))

    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', url=titulo)
    else:
        post = posts[0]
        form.title.data=post.title
        form.content.data=post.content
        return render_template('edit_post.html', form=form)
        '''
        return render_template('error.html', mensaje="Prueba "+form.title.data)
        '''

@app.route('/posts/save', methods = ['GET', 'POST'])
@login_required
def save_post():
    form = PostForm()
    q = db.Query(Post)
    if form.validate_on_submit():
        posts = q.filter('title =', form.title.data)
        if posts.count() == 0:
            return render_template('error.html', mensaje="No se encontro el post editado")
        else:
            post = posts[0]
            db.delete(post.key())
            post1 = Post(title = form.title.data,
                    content = Markup(form.content.data).unescape(),
                    author = users.get_current_user())
            post1.put()
            flash('Entrada actualizada en la base de datos.')
    return redirect(url_for('list_posts'))



@app.route('/posts/delete', methods = ['GET', 'POST'])
@login_required
def delete_post():
    form = PostDelForm()
    q = db.Query(Post)
    if form.validate_on_submit():
        posts = q.filter('title =', form.title.data)
        if posts.count() == 0:
            return render_template('error.html', mensaje="No se encontro el post editado ["+form.title.data+"]")
        else:
            post = posts[0]
            db.delete(post.key())
            flash('Entrada eliminada de la base de datos.')
            return redirect(url_for('list_posts'))

    return render_template('del_post.html', form=form)


@app.route('/posts/del/<string:titulo>/', methods = ['GET', 'POST'])
@login_required
def del_post(titulo):
    form = PostDelForm()
    q = db.Query(Post)
    if form.validate_on_submit():
        posts = q.filter('title =', titulo)
        if posts.count() == 0:
            return render_template('error.html', mensaje="No se encontró el post editado")
        else:
            post = posts[0]
            flash(post.key())
            db.delete(post.key())
            flash('Entrada eliminada de la base de datos.')
            #return redirect(url_for('list_posts'))

    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', url=titulo)
    else:
        post = posts[0]
        form.title.data=post.title
        form.content.data=post.content
        return render_template('del_post.html', form=form)
        '''
        return render_template('error.html', mensaje="Prueba "+form.title.data)
        '''


