from google.appengine.ext import db


class Configuracion(db.Model):
    nombre = db.StringProperty(required = True)
    valor = db.TextProperty(required = True)
    

class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    when = db.DateTimeProperty(auto_now_add = True)
    author = db.UserProperty(required = True)
    etiquetas = db.StringListProperty()
    noticia = db.BooleanProperty()

class Modulo(db.Model):
    id = db.IntegerProperty(required=True)
    titulo = db.StringProperty(required = True)
    descripcion = db.TextProperty(required = True)
    inicio = db.DateTimeProperty(required = True)
    final = db.DateTimeProperty(required = True)
    etiquetas = db.StringListProperty()
    
