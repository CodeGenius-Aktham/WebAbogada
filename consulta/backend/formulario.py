from flask import Flask, request, jsonify # Importacion de la libreria Flask.
from flask_cors import CORS # Comunicacion entre backend y fronted.
from psycopg2 import IntegrityError # Importacion de la libreria que es el adaptador de postgresql y sus errores.
from dotenv import load_dotenv # Ayuda a cargar las variables de entorno del archivo .env
import psycopg2 # Importacion de la libreria que maneja la base de datos.
import re # Validacion del correo electronico.
import os # Manejo interno del archivo .env

# Identificador de la aplicacion.
app = Flask(__name__)
CORS(app,origins='ejemplo.com',supports_credentials=True) # URL del fronted con credenciales para hacer peticiones.

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
            sslmode =  os.getenv('DB_SSL')
        )
        return conn # Retorno de la conexion
    except Exception as error:
        print(f"error de conexion con la base de datos : {error}.")
        return None
    except IntegrityError as error:
        conn.rollback() # Se deshacen los cambios si la conexion falla.
        return jsonify({'error' : 'error de integridad con la base de datos.'}),400

# Ingreso del formulario del cliente.
# Ingreso y enrutador de los clientes.
@app.route('/customer', methods=['POST'])
def ingreso_caso():
    # Convierte la informacion en un archivo json.
    data = request.get_json()

    # Ingreso de los datos del usuario.
    nombre_cliente = data.get('nombre','').strip()
    apellido_cliente =  data.get('apellido','').strip()
    correo_usuario = data.get('correo', '').strip()
    mensaje_usuario =  data.get('mensaje','').strip()

    # Validador de email con regex.
    validador_email =  r"[a-zA-Z0-9_]+([.][a-zA-Z0-9_]+)*@[a-zA-Z0-9_]+([.][a-zA-Z0-9_]+)*[.][a-zA-Z]{2,5}"

    # Validacion de campos tanto de ingreso y del email.
    if not all[(nombre_cliente,apellido_cliente,correo_usuario,mensaje_usuario)]:
        return jsonify({'error' : 'todos los campos deben estar completos'}), 400
    elif not re.fullmatch(validador_email,correo_usuario):
        return jsonify({'error' : 'el email ingreado no es correcto'}),400
    
    # Toma la coexion de la base de datos.
    conn = conexion_db()
    if not conn:
        return jsonify({'error' : 'no se pudo conectar con la base de datos'}),400

    try:
        cursor = conn.cursor() # Cursor para manejo de la base de datos.
        # Ingreso del formulario pedido a la base de datos.
        cursor.execute('''INSERT INTO clientes(nombre_cliente,apellido_cliente,correo_usuario,mensaje_usuario)
                        VALUES (%s,%s,%s,%s)''',(nombre_cliente,apellido_cliente,correo_usuario,mensaje_usuario))
        # Se suben los cambios a la base de datos.
        conn.commit()
        return jsonify({'mensaje' : 'Ingreso del formulario correcto'}),200
    # Manejo de errores.
    except psycopg2.errors.UniqueViolation:
        conn.rollback() # Deshace los cambios en la base de datos si la conexion falla.
        return jsonify({'error' : 'error de validacion de los datos'}),400
    except Exception as error:
        return jsonify({'error' : f'error inesperado en el sistema : {str(error)}'}),400
    finally:
        cursor.close() # Cierra el cursor.
        conn.close() # Cierra la conexion con la base de datos.