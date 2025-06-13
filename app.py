from flask import session
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime # Importa las librerias para la fecha y hora de los mensajes que se envían

from flask_mail import Mail, Message # Esta línea se añadió para el envío de correos electrónicos

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mensajes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de datos
class Mensaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow) # Campo para almacenar la fecha y hora del mensaje

    def __repr__(self):
        return f'<Mensaje {self.nombre}>'

# Ruta principal
@app.route('/')
def inicio():
    mensajes = Mensaje.query.order_by(Mensaje.id.desc()).limit(5).all()
    return render_template('index.html', mensajes=mensajes)

# Ruta "Acerca de"
@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    error = None
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        contenido = request.form['mensaje'].strip()
        
        if len(nombre) < 3 or len(contenido) < 5:
            error = "Por favor, asegúrate de llenar todos los campos correctamente."
        else:
            nuevo_mensaje = Mensaje(nombre=nombre, contenido=contenido)
            db.session.add(nuevo_mensaje)
            db.session.commit()
            # Enviar correo electrónico al administrador
            mensaje_mail = Message("Nuevo mensaje de contacto",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]
            )
            mensaje_mail.body = f'Nombre: {nombre}\nMensaje: {contenido}'
            mail.send(mensaje_mail)
            ###########
            return redirect(url_for('inicio'))

    return render_template('contacto.html', error=error)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'carlos.carbonell250@gmail.com'
app.config['MAIL_PASSWORD'] = 'ruxb jjfv myap eere'
mail = Mail(app)



#Ruta para galeria de imágenes
@app.route('/galeria')
def galeria():
    return render_template('galeria.html')





##ruta de inicio de sesión###############################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if usuario == 'admin' and contrasena == '1234':
            session['logueado'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Credenciales incorrectas'
    return render_template('login.html', error=error)



#ruta de cierre de sesión
@app.route('/logout')
def logout():
    session.pop('logueado', None)
    return redirect(url_for('inicio'))

app.secret_key = 'clave_secreta_educativa_123'

#Ruta de administración
@app.route('/admin')
#def admin():
#    todos_mensajes = Mensaje.query.order_by(Mensaje.id.desc()).all()
#    return render_template('admin.html', mensajes=todos_mensajes)
def admin():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    mensajes = Mensaje.query.order_by(Mensaje.id.desc()).all()
    return render_template('admin.html', mensajes=mensajes)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    mensaje = Mensaje.query.get_or_404(id)
    db.session.delete(mensaje)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea la base de datos si no existe
    app.run(debug=True)



