import shutil
import barcode
from datetime import date
from datetime import datetime
from barcode.writer import ImageWriter
from PIL import Image
import io
import tempfile
import subprocess
from PIL import ImageWin
import csv



# import barcode
import os
# from barcode.writer import ImageWriter

import firebase_admin
from firebase_admin import credentials, firestore

# Configura la ruta a tu archivo de clave de servicio
cred = credentials.Certificate("regomax-aeaed-firebase-adminsdk-eeush-a0ab89b721.json")

# Inicializa la app de Firebase con la clave de servicio
firebase_admin.initialize_app(cred)

# Inicializa Firestore
db = firestore.client()

stock_ref = db.collection('stock')
entregados_ref = db.collection('entregados')
historico_ref = db.collection('historico')


ULTIMA_FECHA = -1
CODIGO = 0
FECHA = 1
LOTE = 1
INDICE = 7
ARCHIVO =  os.path.abspath("stock.csv")
FECHAS = os.path.abspath("fechas.csv")
ENTREGADO = os.path.abspath("entregado.csv")
STOCK_HISTORICO = os.path.abspath("stock_historico.csv")
codigos = {}
dic_producto = {}
lista_prod = []
codigos_hist = {}
dic_producto_hist = {}
lista_prod_hist = []


def obtener_hora():
    hora = datetime.now()
    hora_formateada = hora.strftime('%H:%M')
    lista_hora = (str(hora_formateada).split(":"))
    hora_larga = ""
    for fecha in lista_hora:
        hora_larga = hora_larga + fecha
    return hora_formateada,hora_larga

def obtener_fecha():
    today = date.today()
    dia_formateado = today.strftime('%y/%m/%d')
    lista_fecha = (str(dia_formateado).split("/"))
   
    fecha_larga = ""
    for fecha in lista_fecha:
        fecha_larga = fecha_larga + fecha

    return dia_formateado, fecha_larga



               
def genBARcode(codigo):
    # Generar el código de barras como objeto PIL Image
    BARCODE = barcode.get_barcode_class('code128')
    codigo_bar = BARCODE(codigo, writer=ImageWriter())
    buffer = io.BytesIO()
    codigo_bar.write(buffer)
    
    # Cargar la imagen desde el buffer en memoria
    buffer.seek(0)
    image = Image.open(buffer)
    
    # Guardar la imagen en un archivo temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    image.save(temp_file.name)

    temp_file.close()  # Importante cerrar el archivo para que esté disponible para otros procesos
    
  
    
    # subprocess.run(['notepad', temp_file.name], check=True)
    subprocess.run(['start', temp_file.name], shell=True, check=True)


def cargar_producto(producto,peso,ubicacion):   
    cod_barra = numer_codigo_barras()
    fecha = obtener_fecha()[0]
    hora = obtener_hora()[0]
    lote = cod_barra[10:12]
   
    agregar_archivo(cod_barra,fecha,hora,lote,producto,peso,ubicacion)
    agregar_hist(cod_barra,fecha,hora,lote,producto,peso,ubicacion)
    genBARcode(cod_barra)
    # # os.startfile(nombre_fichero, "print")
    
    

    
def agregar_archivo(codigo,fecha,hora,lote,producto,peso,ubicacion):
    stock_doc_ref = stock_ref.document()
    stock_doc_ref.set({
    'codigo': codigo,
    'fecha': fecha,
    'hora': hora,
    'lote': lote,
    'producto': producto,
    'peso': peso,
    'ubicacion': ubicacion
    })
def agregar_hist(codigo,fecha,hora,lote,producto,peso,ubicacion):
    historico_doc_ref = historico_ref.document()
    historico_doc_ref.set({
    'codigo': codigo,
    'fecha': fecha,
    'hora': hora,
    'lote': lote,
    'producto': producto,
    'peso': peso,
    'ubicacion': ubicacion
    })



def buscar_producto(cod_prod):     
    productos = stock_ref.where('codigo', '==', cod_prod).stream()
    for producto in productos:
        # Convertir el documento a un diccionario y retornarlo
        return producto.to_dict()

    # Si no se encuentra el producto, retornar None
    return None

def entregar_producto(cod_prod):
    producto = buscar_producto(cod_prod)

    print(cod_prod)
    if producto:
        entregados_ref_doc = entregados_ref.document()
        entregados_ref_doc.set({
            'codigo': producto['codigo'],
            'fecha': producto['fecha'],
            'hora': producto['hora'],
            'numero': producto['lote'],
            'producto': producto['producto'],
            'peso': producto['peso'],
            'fecha_entrega': obtener_fecha()[0],
            'hora_entrega':  obtener_hora()[0]
        })
        producto_ref = stock_ref.where('codigo', '==', cod_prod).stream()
        for prod in producto_ref:
            prod.reference.delete()
        return True
    else:
        return False




def borrar_coleccion(coleccion_ref, batch_size=500):
    docs = coleccion_ref.limit(batch_size).stream()
    for doc in docs:
        doc.reference.delete()

def numer_codigo_barras():
    fecha_actual = datetime.now().strftime("%y%m%d")
    hora_actual = datetime.now().strftime("%H%M")
    doc_ref = db.collection('codigos_barras').document(fecha_actual)
    doc = doc_ref.get()
    if doc.exists:
        datos = doc.to_dict()
        ultimo_lote = int(datos['ultimo_lote']) + 1
    else:
        borrar_coleccion(db.collection('codigos_barras'))
        ultimo_lote = 1

    # Actualizar Firestore
    doc_ref.set({'ultimo_lote': f"{ultimo_lote:02}"})

    # Generar código de barras
    codigo_barras = f"{fecha_actual}{hora_actual}{ultimo_lote:02}"
    return codigo_barras
        


def modificar_archivos(cod_prod,posicion_a_mod,dato_modificado):
    producto_ref = stock_ref.where('codigo', '==', cod_prod).stream()
    producto_ref_hist = historico_ref.where('codigo', '==', cod_prod).stream()
    print(posicion_a_mod)
    print(dato_modificado)
    for prod in producto_ref_hist:
        prod.reference.update({posicion_a_mod: dato_modificado})
    for prod in producto_ref:
        prod.reference.update({posicion_a_mod: dato_modificado})
    return True


    



def reimp_cod(cod):
    producto = buscar_producto(cod)
    if producto:
        genBARcode(cod)
        return True
    else:
        False

import csv

def descargar_datos_a_csv(nombre_coleccion, nombre_archivo_csv):
    # Obtener todos los documentos de la colección
    coleccion_ref = db.collection(nombre_coleccion)
    documentos = coleccion_ref.stream()

    # Crear una lista para almacenar los datos
    datos = []

    # Iterar sobre los documentos y agregar los datos a la lista
    for doc in documentos:
        datos.append(doc.to_dict())

    # Obtener los nombres de los campos (keys) del primer documento
    if datos:
        campos = datos[0].keys()
    else:
        print("No se encontraron documentos en la colección.")
        return

    # Escribir los datos en un archivo CSV
    try:
        with open(nombre_archivo_csv, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)
            escritor_csv.writeheader()
            escritor_csv.writerows(datos)
        print(f"Datos exportados exitosamente a {nombre_archivo_csv}")
    except ValueError as e:
        print(f"Error al escribir en el archivo CSV: {e}")
    except Exception as e:
        print(f"Se produjo un error inesperado: {e}")

        
def cargar_desplegables(arch_ubi,arch_pro,ubi,prod):
    with open(arch_ubi, "r") as f:
        for fila in f:
            if fila != "" :
                fila.rstrip()
                ubi.append(fila.rstrip())
    with open(arch_pro, "r") as f:
        for fila in f:
            if fila != "" :
                
                prod.append(fila.rstrip())
 

def agregar_ubi_prod(arch_ubi,elemento,metodo):
    with open(arch_ubi, metodo) as f:
        f.write(elemento +'\n')



def borrar_agregar_ubi(ubi,prod,arch_prod,arch_ubi,elemento):
    if elemento in ubi:
        ubi.remove(elemento)
        with open(arch_ubi, "w") as f:
            for elementos in ubi:
                 f.write(elementos +'\n')
            
    if elemento in prod:
        prod.remove(elemento)
        with open(arch_prod, "w") as f:
            for elementos in prod:
                 f.write(elementos +'\n')




