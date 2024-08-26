import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import csv
from tqdm import tqdm

# Inicializar Firebase Admin SDK
cred = credentials.Certificate('regomaxultimo-firebase-adminsdk-wejo4-f535e92b5c.json')
firebase_admin.initialize_app(cred)

# Conectar a Firestore
db = firestore.client()
STOCK = "Stock.csv"

# Leer el archivo CSV y cargar los datos en Firestore
def cargar_datos_a_firestore(nombre_archivo_csv, nombre_coleccion):
    with open(nombre_archivo_csv, mode='r', encoding='utf-8') as archivo_csv:
        lector_csv = csv.DictReader(archivo_csv)
        filas = list(lector_csv)
        for fila in tqdm(filas, desc="Cargando datos a Firestore"):
            db.collection(nombre_coleccion).add(fila)

# Cargar los datos del archivo stock.csv a la colección 'historico'
cargar_datos_a_firestore(STOCK, 'stock')