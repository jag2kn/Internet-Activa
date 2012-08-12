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



def general_data():
    datos={}
    
    usuario = users.get_current_user()
    datos["usuario"] = usuario
    
    linksPrincipales = []
    linksPrincipales.append(('/', "Home"))
    linksPrincipales.append(('/Modulos', "Modulos"))
    linksPrincipales.append(('/Foros', "Foros"))
    linksPrincipales.append(('/Nosotros', "Acerca de"))
    datos["menu1"]=linksPrincipales

    modulos=[]
    for i in range(1,8+1):
        modulos.append(('/modulo/'+str(i), "Modulo "+str(i)))
    datos["menu2"] = modulos
    
    linksLaterales = []
    linksLaterales.append(('/Calendario', "Calendario"))
    linksLaterales.append(('/Modulos', "Contacto"))
    linksLaterales.append((url_for('list_posts'), "Todos las entradas"))
    linksLaterales.append((url_for('new_post'), "Nuevo articulo"))
    if usuario:
        linksLaterales.append((users.create_logout_url("/"), "Salir"))
    else:
        linksLaterales.append((users.create_login_url("/"), "Ingresar"))
    datos["menu3"] = linksLaterales
    
    
    return datos



@app.route('/')
def redirect_to_home():
    return redirect('/modulo/1/')


@app.route('/<string:key>', methods=['GET', 'POST'])
def entrada(key):
    q = db.Query(Post)
    posts = q.filter('title =', key)
    if posts.count() == 0:
        return render_template('404.html', d=general_data(),url=key)
    else:
        post = posts[0]
        return render_template('post.html', d=general_data(),post=post)



@app.route('/posts')
def list_posts():
    posts = Post.all().order("-when")
    return render_template('list_posts.html', d=general_data(),posts=posts)


@app.route('/post/<string:titulo>/', methods=['GET', 'POST'])
def post(titulo):
    q = db.Query(Post)
    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', d=general_data(),url=titulo)
    else:
        post = posts[0]
        return render_template('post.html', d=general_data(),post=post)


@app.route('/modulo/<int:id>/', methods=['GET', 'POST'])
def modulo(id):
    titulo = "Titulo"
    descripcion = "Descripcion descripcion descripcion descripcion descripcion descripcion descripcion descripcion descripcion descripcion"
    mes = "Sep"
    dias  = "12/23"
    return render_template('modulo.html', d=general_data(),numero=id, titulo=titulo, descripcion=descripcion, mes=mes, dias=dias)



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
    return render_template('new_post.html', d=general_data(),form=form)


@app.route('/posts/edit/<string:titulo>/', methods = ['GET', 'POST'])
@login_required
def edit_post(titulo):
    form = PostForm()
    q = db.Query(Post)
    if form.validate_on_submit():
        posts = q.filter('title =', titulo)
        if posts.count() == 0:
            return render_template('error.html', d=general_data(),mensaje="No se encontró el post editado")
        else:
            post = posts[0]
            flash(post.key())
            db.delete(post.key())
            post1 = Post(title = form.title.data,
                    content = Markup(form.content.data).unescape(),
                    author = users.get_current_user())
            post1.put()
            flash('Entrada actualizada en la base de datos.')
            return render_template('error.html', d=general_data(),mensaje="Post editado")
            #return redirect(url_for('list_posts'))

    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', d=general_data(),url=titulo)
    else:
        post = posts[0]
        form.title.data=post.title
        form.content.data=post.content
        return render_template('edit_post.html', d=general_data(),form=form)

@app.route('/posts/save', methods = ['GET', 'POST'])
@login_required
def save_post():
    form = PostForm()
    q = db.Query(Post)
    if form.validate_on_submit():
        posts = q.filter('title =', form.title.data)
        if posts.count() == 0:
            return render_template('error.html', d=general_data(),mensaje="No se encontro el post editado")
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
            return render_template('error.html', d=general_data(),mensaje="No se encontro el post editado ["+form.title.data+"]")
        else:
            post = posts[0]
            db.delete(post.key())
            flash('Entrada eliminada de la base de datos.')
            return redirect(url_for('list_posts'))

    return render_template('del_post.html', d=general_data(),form=form)


@app.route('/posts/del/<string:titulo>/', methods = ['GET', 'POST'])
@login_required
def del_post(titulo):
    form = PostDelForm()
    q = db.Query(Post)
    if form.validate_on_submit():
        posts = q.filter('title =', titulo)
        if posts.count() == 0:
            return render_template('error.html', d=general_data(),mensaje="No se encontró el post editado")
        else:
            post = posts[0]
            flash(post.key())
            db.delete(post.key())
            flash('Entrada eliminada de la base de datos.')
            #return redirect(url_for('list_posts'))

    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', d=general_data(),url=titulo)
    else:
        post = posts[0]
        form.title.data=post.title
        form.content.data=post.content
        return render_template('del_post.html', d=general_data(),form=form)


