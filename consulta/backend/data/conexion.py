from flask import Flask,jsonify
from flask_cors import CORS
from psycopg2 import IntegrityError
from dotenv import load_dotenv
import psycopg2
import os

# Identificador de la aplicacion.
app = Flask(__name__)
CORS(app,origins='https://codegenius-aktham.github.io/WebAbogada/',supports_credentials=True) # URL del fronted con credenciales para hacer peticiones.

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
        return jsonify({'error' : f'error de integridad con la base de datos : {str(error)}.'}),400
