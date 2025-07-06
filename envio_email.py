from flask import Flask, request, jsonify # Importacion de la libreria Flask.
from flask_cors import CORS # Comunicacion entre backend y fronted.
from psycopg2 import IntegrityError # Importacion de la libreria que es el adaptador de postgresql y sus errores.
from dotenv import load_dotenv  # Ayuda a cargar las variables de entorno del archivo .env
from email.mime.text import MIMEText # Libreria para manejar mensajes.
import smtplib # Libreria para conectar con el servidor de GMAIL.
import psycopg2 # Importacion de la libreria que maneja la base de datos.
import os # Manejo interno del archivo .env

# Identificador de la aplicacion.
app = Flask(__name__)
CORS(app, CORS="www.ejemplo.com", supports_credentials=True) # URL del fronted con credenciales para hacer peticiones.

load_dotenv() # Carga de las variables de entorno.

# Conexion a la base de datos de clientes.
def conexion_db():
    try:
        # Conexion con la base de datos construida en render donde se hara el despliegue.
        conn = psycopg2.connect(
            host = os.getenv('DB_HOST'),
            dbname = os.getenv('DB_NAME'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            port = os.getenv('DB_PORT'),
            ssl = os.getenv('DB_SSL')
        )
        return conn # Retorno de la conexion
    except IntegrityError as error:
        conn.rollback() # Se deshacen los cambios si la conexion falla.
        print(f"Error de conexion con la base de datos : {error}.")
        return None

# Envio de correo electronico.
# Enrutador para envio de emails.
@app.route('/email', methods = ['POST'])
def envio_email():
    # Convierte la informacion en un archivo json.
    data = request.get_json()

    # Ingreso del cuerpo del mensaje
    destinatario = os.getenv('EMAIL_DESTINO')
    asunto = 'cliente juridico'
    correo_usuario = data.get('correo','').strip()
    mensaje_usuario = data.get('mensaje','').strip()

    # Validador de existencia de los campos.
    if not correo_usuario or not mensaje_usuario:
        return jsonify({'error' : 'el campo debe estar completo.'}),400
    
    # Toma la conexion con la base de datos.
    conn = conexion_db()
    if not conn:
        return jsonify({'error' : 'no se pudo conectar con la base de datos'}),400
    
    try:
        cursor = conn.cursor() # Cursor para manejo de la base de datos.
        # Busqueda del email y mensaje en la base de datos.
        cursor.execute('''SELECT * FROM clientes WHERE correo_usuario = %s AND mensaje_usuario = %s''',(correo_usuario,mensaje_usuario))
        if cursor.fetchone() is None:
            cursor.close() # Cierra el cursor de la base de datos
            conn.close() # Cierra la conexion con la base de datos.
            return jsonify({'error' : 'email y mensaje no encontrado.'}),400
        
        # Crea el cuerpo del correo electronico.
        mensage = MIMEText(mensaje_usuario)
        mensage['Subject'] = asunto
        mensage['From'] = correo_usuario
        mensage['To'] = destinatario

        # Conexion con el servidor de Gmail.
        server = smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.ehlo() # Identifica al servidor.
        server.login(os.getenv('EMAIL_DESTINO'),os.getenv('EMAIL_PASSWORD')) # Inicio del login con el email.
        server.sendmail(correo_usuario,destinatario,mensage.as_string()) # Envio del mensaje
        server.quit() # Cierre del servidor.
        return jsonify({'mensaje' : 'correo enviado correctamente.'}),200
    # Manejo de errores.
    except psycopg2.errors.IntegrityError:
        conn.rollback() # Si falla la conexion borra cualquier cambio.
        return jsonify({'error' : 'error inesperado en el sistema.'}),400
    except Exception as error:
        return jsonify({'error': f'error inesperado en el programa : {str(error)}.'}),400
