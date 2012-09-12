# -*- coding: utf-8 -*-
from blog import app
from models import Post
from decorators import login_required, admin_required, isadmin

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

def get_modulos():
    return {
            1:{
                "titulo":u"Internet, sociedad de información y mecanismos de participación",
                "autor":u"Michael Bowens",
                "institucion":u"P2P Fundation",
                "fecha":"Sep 27"},
            2:{
                "titulo":u"Libertad de expresión",
                "autor":u"",
                "institucion":u"",
                "fecha":"Oct 11"},
            3:{
                "titulo":"Privacidad",
                "autor":u"",
                "institucion":u"",
                "fecha":"Oct 25"},
            4:{
                "titulo":"Derechos de autor y excepciones y limitaciones",
                "autor":u"",
                "institucion":u"",
                "fecha":"Nov 8"},
            5:{
                "titulo":"Gobernanza de Internet",
                "autor":u"",
                "institucion":u"",
                "fecha":"Nov 22"},
            6:{
                "titulo":"Neutralidad de la red",
                "autor":u"",
                "institucion":u"",
                "fecha":"Dic 6"},
            7:{
                "titulo":"Derecho a Acceso",
                "autor":u"",
                "institucion":u"",
                "fecha":"Dic 13"},
            8:{
                "titulo":"Procedimientos para bloqueo de Contenidos en Internet",
                "autor":u"",
                "institucion":u"",
                "fecha":"Ene 17"}
        }
    
    
def get_talleres():
    return {
            1:{
                "titulo":u"Redes sociales para el activismo Talleristas",
                "autor":u"",
                "institucion":u"",#Hacktivistas
                "fecha":"Sep 27"},
            2:{
                "titulo":u"Crowdfounding y mecanismos de financiación Tallersitas",
                "autor":u"",
                "institucion":u"",#Goteo Funding
                "fecha":"Sep 27"},
            3:{
                "titulo":u"Seguridad y privacidad Tallerista",
                "autor":u"",#Daniel Torres
                "institucion":u"RedPaTodos",
                "fecha":"Sep 27"},
            4:{
                "titulo":u"Licenciamiento abierto Tallerista",
                "autor":u"Pilar Sáenz y Maritza Sánchez",
                "institucion":u"Fundación Karisma",
                "fecha":"Sep 27"}
        }
        
def get_auditorios():
    return {
            1:{
                "titulo":u"Hackbo",
                "autor":u"",
                "institucion":u"",#Hackbo
                "fecha":""}
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
    datos["url"]=request.url
    datos["descripcion"]="Internet Activa"
    datos["titulo"]="Internet Activa"
    
    datos['imagenCabecera']='images/ImagenCabecera.png'
    logging.info(request.__dict__)
    logging.info("************* "+request.environ['PATH_INFO'])
    usuario = users.get_current_user()
    logging.info("--------------- "+usuario.email())

    
    usuario = users.get_current_user()
    datos["usuario"] = usuario

    datos["admin"] = isadmin()
    
    linksPrincipales = []
    linksPrincipales.append(('/', "Home"))
    linksPrincipales.append(('/Metodologia', u'Metodología'))
    linksPrincipales.append(('/Foros', "Foros"))
    linksPrincipales.append(('/Nosotros', "Acerca de"))
    datos["menu1"]=linksPrincipales

    datos["modulos"] = get_modulos()
    datos["talleres"] = get_talleres()
    datos["auditorios"] = get_auditorios()
    
    linksLaterales = []
    linksLaterales.append(('/Calendario', "Calendario"))
    linksLaterales.append(('/Contacto', "Contacto"))
    if usuario:
        if isadmin():
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
    titulos=[
        u"Un curso en línea para que activemos la Red"]
        #u"Internet Activa",
        #u"Currículo del primer curso"]
    posts=[]
    
    for t in titulos:
        q = db.Query(Post)
        ps = q.filter('title =', t)
        if not ps.count() == 0:
            posts.append(ps[0])
            
    q = db.Query(Post)
    ps = q.filter('noticia =', True).order('-when')
    for p in ps:
        if not p.title in titulos:
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
    modulos = get_modulos()
    if posts.count() == 0:
        titulo = modulos[id]["titulo"]
        mes,dias = modulos[id]["fecha"].split(" ")
        
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

@app.route('/taller/<int:id>/', methods=['GET', 'POST'])
def taller(id):

    '''
    ToDo: Se utilizo la entidad Post para guardar la información de los modulos
    esto es temporal y solo es para visualizar el template de los modulos con videos
    Implementar entidad Modulo
    '''

    q = db.Query(Post)
    posts = q.filter('title =', "taller_"+str(id))
    descripcion = "ESTAMOS TRABAJANDO EN ESTOS CONTENIDOS ESTAREMOS PUBLICANDO LA INFORMACION MUY PRONTO!"
    dias = "12/23"
    mes = "Sep"
    modulos = get_modulos()
    if posts.count() == 0:
        titulo = modulos[id]["titulo"]
        mes,dias = modulos[id]["fecha"].split(" ")
        
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
    return render_template('taller.html', d=general_data(),numero=id, titulo=titulo, descripcion=descripcion, mes=mes, dias=dias)

@app.route('/auditorio/<string:id>/', methods=['GET', 'POST'])
def auditorio(id):

    '''
    ToDo: Se utilizo la entidad Post para guardar la información de los modulos
    esto es temporal y solo es para visualizar el template de los modulos con videos
    Implementar entidad Modulo
    '''

    q = db.Query(Post)
    posts = q.filter('title =', "auditorio_"+id)
    descripcion = "ESTAMOS TRABAJANDO EN ESTOS CONTENIDOS ESTAREMOS PUBLICANDO LA INFORMACION MUY PRONTO!"
    dias = "12/23"
    mes = "Sep"
    modulos = get_modulos()
    if posts.count() == 0:
        titulo = modulos[id]["titulo"]
        mes,dias = modulos[id]["fecha"].split(" ")
        
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
    return render_template('taller.html', d=general_data(),numero=id, titulo=titulo, descripcion=descripcion, mes=mes, dias=dias)




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
            cuando = post.when
            db.delete(post.key())
            post1 = Post(title = form.title.data,
                    content = Markup(form.content.data).unescape(),
                    author = users.get_current_user(),
                    noticia = form.noticia.data,
                    etiquetas = form.etiquetas.data.split(","),
                    when = cuando)
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


