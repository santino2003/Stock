import shutil
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import tempfile
import os
import csv
from datetime import datetime, timedelta,date
from PIL import ImageWin
import csv
import threading
from google.cloud.firestore_v1.field_path import FieldPath






STOCK_HISTORICO = os.path.abspath("stock_historico.csv")

import firebase_admin
from firebase_admin import credentials, firestore

# Configura la ruta a tu archivo de clave de servicio
cred = credentials.Certificate("regomaxultimo-firebase-adminsdk-wejo4-f535e92b5c.json")

# Inicializa la app de Firebase con la clave de servicio
firebase_admin.initialize_app(cred)

# Inicializa Firestore
db = firestore.client()

stock_ref = db.collection('stock')
entregados_ref = db.collection('entregados')
ultimas_24h_ref = db.collection('ultimas_24h')




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
    # Crear un archivo temporal que se eliminará automáticamente
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            # Generar el código de barras
            BARCODE = barcode.get_barcode_class('code128')
            codigo_bar = BARCODE(codigo, writer=ImageWriter())
            
            # Guardar el archivo en la carpeta temporal
            nombre_fichero = codigo_bar.save(temp_file.name)
            
            # Reemplazar las barras invertidas por barras dobles
            nombre_fichero = nombre_fichero.replace("\\", "//")
            
            print(nombre_fichero)
            # Imprimir el archivo
            os.startfile(nombre_fichero, "print")
            
            # Función para eliminar el archivo después de 15 segundos
            def eliminar_archivo(nombre_fichero):
                threading.Timer(60, os.remove, [nombre_fichero]).start()
            
            # Ejecutar la función de eliminación en paralelo
            eliminar_archivo(nombre_fichero)
        except Exception as e:
            print(f"Error al generar el código de barras: {e}")



def cargar_producto(producto,peso,ubicacion):   
    cod_barra = numer_codigo_barras()
    fecha = obtener_fecha()[0]
    hora = obtener_hora()[0]
    lote = cod_barra[10:12]
   
    agregar_archivo(cod_barra,fecha,hora,lote,producto,peso,ubicacion)
    hist_escritorio(cod_barra,fecha,hora,lote,producto,peso,ubicacion)
    genBARcode(cod_barra)
    
def hist_escritorio(codigo,fecha,hora,lote,producto,peso,ubicacion): 
    with open(STOCK_HISTORICO, "a") as f:
        f.write(codigo +","+fecha +","+ hora +","+ lote +","+ producto +","+ peso +","+ubicacion+'\n')
    copiar(STOCK_HISTORICO)
def copiar(archivo):
    user_profile = os.environ['USERPROFILE']
    posibles_rutas = [
        os.path.join(user_profile, 'OneDrive', 'Desktop'),
        os.path.join(user_profile, 'OneDrive', 'Escritorio'),
        os.path.join(user_profile, 'Desktop'),
        os.path.join(user_profile, 'Escritorio')
    ]

    # Encontrar la ruta válida
    escritorio = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            escritorio = ruta
            break
    shutil.copy(archivo,escritorio)
    
def agregar_archivo(codigo, fecha, hora, numero, producto, peso, ubicacion):
    stock_doc_ref = db.collection('stock').document(codigo)
    stock_doc_ref.set({
        'codigo': codigo,
        'fecha': fecha,
        'hora': hora,
        'numero': numero,
        'producto': producto,
        'peso-Kg': peso,
        'ubicacion/Precinto': ubicacion
    })


def buscar_producto(cod_prod):     
    productos = stock_ref.where('codigo', '==', cod_prod).stream()
    for producto in productos:
        # Convertir el documento a un diccionario y retornarlo
        return producto.to_dict()

    # Si no se encuentra el producto, retornar None
    return None

def entregar_producto(cod_prod,cliente):
    producto = buscar_producto(cod_prod)
    if producto:
        entregados_ref_doc = entregados_ref.document()
        entregados_ref_doc.set({
            'codigo': producto['codigo'],
            'fecha': producto['fecha'],
            'hora': producto['hora'],
            'numero': producto['numero'],
            'producto': producto['producto'],
            'peso': producto['peso-Kg'],
            'fecha_entrega': obtener_fecha()[0],
            'hora_entrega':  obtener_hora()[0],
            'cliente': cliente
        })
        producto_ref = stock_ref.where('codigo', '==', cod_prod).stream()
        entregar_ultmas_24h(producto,cliente)
        for prod in producto_ref:
            prod.reference.delete()
        return True
    else:
        return False
    
def obtener_fecha_actual():
    return datetime.utcnow().strftime('%Y-%m-%d')

def verificar_y_eliminar_coleccion_si_cambia_dia(coleccion_ref, fecha_actual):
    # Obtener el documento que almacena la última fecha de actualización
    fecha_doc_ref = db.collection('metadata').document('ultima_fecha')
    fecha_doc = fecha_doc_ref.get()

    if fecha_doc.exists:
        ultima_fecha = fecha_doc.to_dict().get('fecha')
        if ultima_fecha != fecha_actual:
            # Eliminar la colección si la fecha ha cambiado
            borrar_coleccion(coleccion_ref)
            # Actualizar la última fecha de actualización
            fecha_doc_ref.set({'fecha': fecha_actual})
    else:
        # Si el documento no existe, crearlo con la fecha actual
        fecha_doc_ref.set({'fecha': fecha_actual})

def entregar_ultmas_24h(producto, cliente):
    # Obtener la fecha actual
    fecha_actual = obtener_fecha_actual()

    # Referencia a la colección de las últimas 24 horas
    ultimas_24h_ref = db.collection('ultimas_24h')

    # Verificar si la fecha ha cambiado y eliminar la colección si es necesario
    verificar_y_eliminar_coleccion_si_cambia_dia(ultimas_24h_ref, fecha_actual)

    # Agregar el nuevo documento a la colección
    ultimas_24h_doc_ref = ultimas_24h_ref.document(producto['codigo'])
    ultimas_24h_doc_ref.set({
        'codigo': producto['codigo'],
        'fecha': producto['fecha'],
        'hora': producto['hora'],
        'numero': producto['numero'],
        'producto': producto['producto'],
        'peso': producto['peso-Kg'],
        'fecha_entrega': obtener_fecha()[0],
        'hora_entrega': obtener_hora()[0],
        'cliente': cliente
    })

    


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
        


def modificar_archivos(cod_prod, nuevos_datos):
    # Obtener la referencia del documento que coincide con el código del producto
    producto_ref = stock_ref.where('codigo', '==', cod_prod).limit(1).stream()
    
    # Convertir el stream a una lista para obtener el primer (y único) documento
    producto_list = list(producto_ref)
    
    if not producto_list:
        print(f"No se encontró el producto con código: {cod_prod}")
        return False
    
    # Obtener la referencia del primer documento
    prod = producto_list[0]
    
    # Obtener los datos actuales del documento
    datos_actuales = prod.to_dict()
    
    # Modificar los campos necesarios
    for key, value in nuevos_datos.items():
        datos_actuales[key] = value
    
    # Sobrescribir todo el documento con los datos actualizados
    prod.reference.set(datos_actuales)
    
    return True



def reimp_cod(cod):
    producto = buscar_producto(cod)
    if producto:
        genBARcode(cod)
        return True
    else:
        False



def descargar_datos_a_csv(nombre_coleccion, nombre_archivo_csv, campo_fecha):
    # Obtener todos los documentos de la colección
    coleccion_ref = db.collection(nombre_coleccion)
    documentos = coleccion_ref.stream()

    # Crear una lista para almacenar los datos
    datos = []

    # Iterar sobre los documentos y agregar los datos a la lista
    for doc in documentos:
        datos.append(doc.to_dict())

    # Convertir las fechas de cadena a objetos datetime y ordenar los datos
    try:
        datos.sort(key=lambda x: datetime.strptime(x.get(campo_fecha), '%y/%m/%d'), reverse=True)
    except ValueError as e:
        print(f"Error al convertir las fechas: {e}")
        return

    # Obtener los nombres de los campos (keys) del primer documento
    if datos:
        campos = datos[0].keys()
    else:
        print("No se encontraron documentos en la colección.")
        return

    # Construir la ruta completa al escritorio del usuario
    user_profile = os.environ['USERPROFILE']
    posibles_rutas = [
        os.path.join(user_profile, 'OneDrive', 'Desktop'),
        os.path.join(user_profile, 'OneDrive', 'Escritorio'),
        os.path.join(user_profile, 'Desktop'),
        os.path.join(user_profile, 'Escritorio')
    ]

    # Encontrar la ruta válida
    escritorio = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            escritorio = ruta
            break

    if escritorio is None:
        print("No se encontró la ruta al escritorio.")
        return

    ruta_archivo_csv = os.path.join(escritorio, nombre_archivo_csv)

    # Escribir los datos en un archivo CSV
    try:
        with open(ruta_archivo_csv, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)
            escritor_csv.writeheader()
            escritor_csv.writerows(datos)
        print(f"Datos exportados exitosamente a {ruta_archivo_csv}")
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




