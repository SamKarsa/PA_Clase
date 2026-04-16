import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_COLLECTION = os.getenv("DATABASE_COLLECTION")

class DatabaseClient:
    def __init__(self, database_name=DATABASE_NAME , collection_name=DATABASE_COLLECTION):
        if MONGO_USER and MONGO_PASSWORD and MONGO_HOST:
            self.connection_string = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}/"
        else:
            raise ValueError("Error: Faltan variables MONGO_USER, MONGO_PASSWORD o MONGO_HOST en .env")
        
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    def conectar(self):
        try:
            # Crear cliente de MongoDB
            print(f"🔌 Conectando a MongoDB Atlas...")
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000
            )

            # Verificar que la conexión funcione
            self.client.server_info()

            # Seleccionar base de datos y colección
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]

            print(f"✅ Conectado a MongoDB exitosamente")
            print(f"📊 Base de datos: {self.database_name}")
            print(f"📁 Colección: {self.collection_name}")
            
            return True
        
        except ServerSelectionTimeoutError:
            print(f"Error: No se pudo conectar al servidor de MongoDB")
            print(f"   Verifica tu connection string y tu conexión a internet")
            return False
            
        except ConnectionFailure:
            print(f"Error: Fallo en la conexión a MongoDB")
            return False
            
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False

    def insertar_datos(self, datos):
        if self.collection is None:
            print(f"Error: No hay conexión a MongoDB. Llama a conectar() primero")
            return 0
        
        if not datos or len(datos) == 0:
            print(f"No hay datos para insertar")
            return 0
        
        try:
            print(f"Insertando {len(datos)} documentos en MongoDB...")
            
            # Agregar timestamp a cada documento
            for documento in datos:
                documento['_fecha_insercion'] = datetime.now()
            
            # Insertar todos los documentos
            resultado = self.collection.insert_many(datos)
            
            cantidad_insertada = len(resultado.inserted_ids)
            
            print(f"✅ Se insertaron {cantidad_insertada} documentos exitosamente")
            
            return cantidad_insertada
            
        except Exception as e:
            print(f"Error al insertar datos: {e}")
            return 0
        
    def limpiar_coleccion(self):
        if self.collection is None:
            print(f"Error: No hay conexión a MongoDB")
            return 0
    
        try:
            print(f"Limpiando colección {self.collection_name}...")
            resultado = self.collection.delete_many({})
            print(f"Se eliminaron {resultado.deleted_count} documentos")
            return resultado.deleted_count
        except Exception as e:
            print(f"Error al limpiar colección: {e}")
            return 0
        
    
    def consultar_datos(self, filtro=None, limite=100):
        if self.collection is None:
            print(f"Error: No hay conexión a MongoDB")
            return []
        
        try:
            if filtro is None:
                filtro = {}
            
            print(f"Consultando datos de MongoDB...")
            
            cursor = self.collection.find(filtro).limit(limite)
            datos = list(cursor)
            
            print(f"Se encontraron {len(datos)} documentos")
            
            return datos
            
        except Exception as e:
            print(f"Error al consultar datos: {e}")
            return []

    def contar_documentos(self, filtro=None):
        if self.collection is None:
            print(f"Error: No hay conexión a MongoDB")
            return 0
        
        try:
            if filtro is None:
                filtro = {}
            cantidad = self.collection.count_documents(filtro)
            print(f"Total de documentos: {cantidad}")
            return cantidad
            
        except Exception as e:
            print(f"Error al contar documentos: {e}")
            return 0
        
    def desconectar(self):
        if self.client:
            self.client.close()
            print(f"Desconectado de MongoDB")

        
