# -*- coding: utf-8 -*-
from blog import app
from models import Post
from decorators import login_required, admin_required

from flask import render_template, flash, url_for, redirect
from flaskext import wtf
from flaskext.wtf import validators
from flask import request

from google.appengine.api import users
from google.appengine.ext import db

from jinja2 import Markup
import logging


providers = {
    'Google'   : 'www.google.com/accounts/o8/id', # shorter alternative: "Gmail.com"
    'Yahoo'    : 'yahoo.com',
    'MySpace'  : 'myspace.com',
    'AOL'      : 'aol.com',
    'MyOpenID' : 'myopenid.com'
    # add more here
}


class PostForm(wtf.Form):
    title = wtf.TextField('Title', validators=[validators.Required()])
    title_old = wtf.HiddenField()
    content = wtf.TextAreaField('Content', validators=[validators.Required()])
    etiquetas = wtf.TextAreaField('Etiquetas')
    noticia = wtf.BooleanField('Noticia')


class PostDelForm(wtf.Form):
    title = wtf.HiddenField('Title', validators=[validators.Required()])
    content = wtf.HiddenField('Content', validators=[validators.Required()])



def general_data():
    datos={}
    
    datos["servidor"]=request.url.replace("/", "").split(":")[1]

    
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
    if usuario:
        if users.is_current_user_admin():
            linksLaterales.append((url_for('list_posts'), "Todos las entradas"))
            linksLaterales.append((url_for('new_post'), "Nuevo articulo"))
        linksLaterales.append((users.create_logout_url("/"), "Salir"))
    else:
        linksLaterales.append((users.create_login_url("/"), "Ingresar"))
    datos["menu3"] = linksLaterales
    
    return datos


@app.route('/')
def redirect_to_home():
    return redirect('/Inicio')

@app.route('/Inicio')
def inicio():
    titulos=[""]
    posts=[]
    
    for t in titulos:
        q = db.Query(Post)
        ps = q.filter('title =', t)
        if not ps.count() == 0:
            posts.append(ps[0])
            
    q = db.Query(Post)
    ps = q.filter('noticia =', True).order('-when')
    for p in ps:
        posts.append(p)
        
    return render_template('list_posts.html', d=general_data(),posts=posts)


@app.route('/openid', methods=['GET', 'POST'])
def openid():
    links=[]

    for name, uri in providers.items():
        links.append((users.create_login_url('/',federated_identity=uri),name))
        #links.append((uri,name))
    return render_template('login.html', d=general_data(),links=links)



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


@app.route('/tag/<string:tag>/', methods=['GET', 'POST'])
def post(tag):
    q = db.Query(Post)
    posts = q.filter('etiquetas IN ', [tag])
    return render_template('list_posts.html', d=general_data(),posts=posts)


@app.route('/modulo/<int:id>/', methods=['GET', 'POST'])
def modulo(id):

    '''
    ToDo: Se utilizo la entidad Post para guardar la información de los modulos
    esto es temporal y solo es para visualizar el template de los modulos con videos
    Implementar entidad Modulo
    '''

    q = db.Query(Post)
    posts = q.filter('title =', "modulo_"+str(id))
    descripcion = "ESTAMOS TRABAJANDO EN ESTOS CONTENIDOS ESTAREMOS PUBLICANDO LA INFORMACION MUY PRONTO!"
    dias = "12/23"
    mes = "Sep"
    if posts.count() == 0:
        titulos={
            2:"Libertad de expresi&oacute;n",
            3:"Privacidad",
            4:"Derechos de autor y excepciones y limitaciones",
            5:"Gobernanza de Internet",
            6:"Neutralidad de la red",
            7:"Derecho a Acceso",
            8:"Procedimientos para bloqueo de Contenidos en Internet"
            }
        titulo = titulos[id]
    else:
        post=posts[0]
        datos=post.content.split("|")
        titulo = datos[0].replace("<p>", "").replace("</p>", "")
        if len(datos)>1:
            mes = datos[1]
        if len(datos)>2:
            dias = datos[2]
        if len(datos)>3:
            descripcion = datos[3]
    return render_template('modulo.html', d=general_data(),numero=id, titulo=titulo, descripcion=descripcion, mes=mes, dias=dias)



@app.route('/posts/new', methods = ['GET', 'POST'])
@admin_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data,
                    content = Markup(form.content.data).unescape(),
                    author = users.get_current_user(),
                    noticia = form.noticia.data,
                    etiquetas = form.etiquetas.data.replace(" ", "").split(","))
        post.put()
        flash('Entrada guardada en la base de datos.')
        return redirect(url_for('list_posts'))
    return render_template('new_post.html', d=general_data(),form=form)


@app.route('/posts/edit/<string:titulo>/', methods = ['GET', 'POST'])
@admin_required
def edit_post(titulo):
    form = PostForm()
    q = db.Query(Post)
    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', d=general_data(),url=titulo)
    else:
        post = posts[0]
        form.title.data=post.title
        form.title_old.data=post.title
        form.content.data=post.content
        form.etiquetas.data=(",").join(post.etiquetas).replace(" ", "")
        form.noticia.data=post.noticia
        return render_template('edit_post.html', d=general_data(),form=form)

@app.route('/posts/save', methods = ['GET', 'POST'])
@admin_required
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
                    author = users.get_current_user(),
                    noticia = form.noticia.data,
                    etiquetas = form.etiquetas.data.split(","))
            post1.put()
            flash('Entrada actualizada en la base de datos.')
            #ToDo: hacer redireccion al post editado
    return redirect(url_for('list_posts'))



@app.route('/posts/delete', methods = ['GET', 'POST'])
@admin_required
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
@admin_required
def del_post(titulo):
    form = PostDelForm()
    q = db.Query(Post)
    posts = q.filter('title =', titulo)
    if posts.count() == 0:
        return render_template('404.html', d=general_data(),url=titulo)
    else:
        post = posts[0]
        form.title.data=post.title
        form.content.data=post.content
        return render_template('del_post.html', d=general_data(),form=form)


