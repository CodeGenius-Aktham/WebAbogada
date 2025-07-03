from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2 import IntegrityError
from dotenv import load_dotenv
import psycopg2
import re
import os

app = Flask(__name__)
CORS(app,origins='ejemplo.com',supports_credentials=True)

load_dotenv()

def conexion_db():
    try:
        conn = psycopg2.connect(
            host = os.getenv('DB_HOST'),
            name = os.getenv('DB_NAME'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            port = os.getenv('DB_PORT'),
            ssl =  os.getenv('DB_SSL')
        )
        return conn
    except IntegrityError as error:
        conn.rollback()
        print(f"Error de conexion con la base de datos: {error}.")
        return None

@app.route('/customer', methods=['POST'])
def ingreso_caso():
    data = request.get_json()

    nombre_cliente = data.get('nombre','').strip()
    apellido_cliente =  data.get('apellido','').strip()
    correo_usuario = data.get('correo', '').strip()
    mensaje_usuario =  data.get('mensaje','').strip()

    validador_email =  r"[a-zA-Z0-9_]+([.][a-zA-Z0-9_]+)*@[a-zA-Z0-9_]+([.][a-zA-Z0-9_]+)*[.][a-zA-Z]{2,5}"

    if not all[(nombre_cliente,apellido_cliente,correo_usuario,mensaje_usuario)]:
        return jsonify({'error' : 'todos los campos deben estar completos'}), 400
    elif not re.fullmatch(validador_email,correo_usuario):
        return jsonify({'error' : 'el email ingreado no es correcto'}),400
    
    conn = conexion_db()
    if not conn:
        return jsonify({'error' : 'no se pudo conectar con la base de datos'})
    try:
        cusor = conn.cursor()
        cusor.execute('''INSERT INTO clientes(nombre_cliente,apellido_cliente,correo_usuario,mensaje_usuario)
                        VALUES (%s,%s,%s,%s)''',(nombre_cliente,apellido_cliente,correo_usuario,mensaje_usuario))
        conn.commit()
        return jsonify({'mensaje' : 'Ingreso del formulario correcto'}),200
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({'error' : 'error de validacion de los datos'}),400
    except Exception as error:
        return jsonify({'error' : f'error inesperado en el sistema : {str(error)}'}),400
    finally:
        cusor.close()
        conn.close()