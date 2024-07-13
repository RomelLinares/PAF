from flask import Flask, jsonify, request
from markupsafe import escape
from bd import obtenerconexion
from flask_jwt import JWT, jwt_required, current_identity
import controladores.controlador_users as controlador_users

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id



def authenticate(username, password):
    # user = username_table.get(username, None)
    user = None
    userfrombd = controlador_users.obtener_user_username(username)
    if userfrombd is not None:
        user = User(userfrombd["id"], userfrombd["email"], userfrombd["password"])
    if user is not None and (user.password.encode('utf-8') == password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    # return userid_table.get(user_id, None)
    userfrombd = controlador_users.obtener_user_id(user_id)
    user = User(userfrombd["id"], userfrombd["email"], userfrombd["password"])
    return user

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/<nombre>")
def saludar(nombre):
    return f"<p>Hola, {escape(nombre)}!</p>"

@app.route("/probandogeneracionjson")
def probandogeneracionjson():
    beatles = ['John', 'Paul', 'George', 'Ringo']
    pinkfloyd = {
                    "bajo" : "Roger Waters",
                    "bateria" : "Nick Mason",
                    "guitarra" : "David Gilmour",
                    "teclados" : "Richard Wright",
                    "soporte" : beatles
                }
    return jsonify(pinkfloyd)

@app.route("/probandoconexion")
def probandoconexion():
    try:
        connection = obtenerconexion()
        with connection:
            with connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
                cursor.execute(sql, ('jperez@uss.edu.pe', 'very-secret'))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()
        return "Conexión exitosa. Registro exitoso"
    except:
        return "Problemas en la conexión"

@app.route("/api_leerusuarios")
def api_leerusuarios():
    rpta = dict()
    connection = obtenerconexion()
    with connection:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `password` FROM `users`"
            cursor.execute(sql)
            result = cursor.fetchall()
    rpta["code"] = 1
    rpta["message"] = "Lectura correcta de usuarios"
    rpta["detalle"] = result
    return jsonify(rpta)

@app.route("/api_leerproductos")
@jwt_required()
def api_leerproductos():
    rpta = dict()
    connection = obtenerconexion()
    with connection:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `title`, `url`, `price` FROM `products`"
            cursor.execute(sql)
            result = cursor.fetchall()
    rpta["code"] = 1
    rpta["message"] = "Lectura correcta de productos"
    rpta["data"] = result
    return jsonify(rpta)

@app.route("/api_insertarusuario", methods=['POST'])
def api_insertarusuario():
    email = request.json["email"]
    password = request.json["password"]
    connection = obtenerconexion()
    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
            cursor.execute(sql, (email, password))
        connection.commit()
    return jsonify("{'code':1, 'message':'Inserción correcta', 'data':[]}")

@app.route("/api_actualizarusuario", methods=['POST'])
def api_actualizarusuario():
    id = request.json["id"]
    email = request.json["email"]
    password = request.json["password"]
    connection = obtenerconexion()
    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "UPDATE `users` SET `email`=%s, `password`=%s WHERE `id`=%s"
            cursor.execute(sql, (email, password, id))
        connection.commit()
    return jsonify("{'code':1, 'message':'Actualización correcta', 'data':[]}")

# Queda pendiente agregar JWT y Retrofit


@app.route('/registrar', methods=['POST'])
def registrar():
    connection = obtenerconexion()
    dni = request.json['dni']
    nombre_completo = request.json['nombre_completo']
    nota_examen = request.json['nota_examen']
    nota_proyecto = request.json['nota_proyecto']

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO alumnos (dni, nombre_completo, nota_examen, nota_proyecto) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (dni, nombre_completo, nota_examen, nota_proyecto))
        connection.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/resumen', methods=['GET'])
def resumen():
    connection = obtenerconexion()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(nota_examen * 0.6 + nota_proyecto * 0.4) AS max_nota, MIN(nota_examen * 0.6 + nota_proyecto * 0.4) AS min_nota, AVG(nota_examen * 0.6 + nota_proyecto * 0.4) AS avg_nota, COUNT(*) AS num_alumnos FROM alumnos")
            result = cursor.fetchone()
            resumen = f"Nota de curso más alta: {result['max_nota']}\nNota de curso más baja: {result['min_nota']}\nPromedio de notas de curso: {result['avg_nota']} de {result['num_alumnos']} alumnos registrados."
            return jsonify({'resumen': resumen})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/nombre', methods=['GET'])
def nombre():
    return jsonify({'nombre': 'Ramos Suarez Linder Jesus'})


