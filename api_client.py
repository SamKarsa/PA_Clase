import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_URL = os.getenv("API_URL")

class APIClient:
    def __init__(self, url=API_URL):
        self.url = url

    def consultar(self, limite=100):
        try:
            response = requests.get(self.url, params={'$limit': limite}, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"❌ Error: La petición tardó más de 30 segundos")
            return None
        except requests.exceptions.RequestException as e:
            print (f"error en la consulta: {e}")
            return None
            
