import asyncio
import json
import base64
import io
import os
import threading
import random
import string

#Para menejo de imágenes
from PIL import Image
import imagehash

#Para comunicación con la página web
import websockets

#Para hostear página index.html en localhost
from http.server import HTTPServer, SimpleHTTPRequestHandler

#Variable global para guardar datos con Hamming
tramasOriginalEnHamming = []
tramasCorrompidaEnHamming = []
posicionesErrores = []
simbolosRecuperados = []
simbolosCorrompidos = []
bitsDeError = []

# HTTP index
class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)

def iniciar_http():
    servidor = HTTPServer(("localhost", 8000), FrontendHandler)
    print("http://localhost:8000")
    servidor.serve_forever()



# Compresión
def comprimir_imagen(original_b64, comprimido_b64, original_bytes, comprimido_bytes, ruido, formato, posicion, distribucionErrores, cantidadErrores):
    
    global tramasOriginalEnHamming
    global tramasCorrompidaEnHamming
    global posicionesErrores
    global simbolosRecuperados
    global simbolosCorrompidos
    global bitsDeError
    
    #Meter ruido en la comunicación (modificar bytes de la foto comprimida)
    print()
    recuperada_b64 = 0
    comprimido_b64_original = comprimido_b64
    if ruido:
        print("corrompiendo valores de imagen comprimida...")
        comprimido_b64 = corromper(comprimido_b64, posicion, distribucionErrores, cantidadErrores)
        recuperada_b64 = recuperarImagenCorrompida(comprimido_b64)
        if recuperada_b64 == comprimido_b64_original:
            print(">> Las recuperación fue exitosa\n")
    #Fin ruido

    tam_original = len(original_bytes)
    tam_comprimido = len(comprimido_bytes)

    reduccion = ( 100 - (tam_comprimido * 100 / tam_original) )
    
    
    #Comparar imagenes por hash
    img_bytes1 = base64.b64decode(original_b64)
    
    # Convertir los bytes a objetos de imagen Pillow
    img1 = Image.open(io.BytesIO(img_bytes1))
    
    # Calcular el hash perceptual (pHash) para ambas imágenes
    hash1 = imagehash.phash(img1)
    
    try:
        img_bytes2 = base64.b64decode(comprimido_b64)
        img2 = Image.open(io.BytesIO(img_bytes2))
        hash2 = imagehash.phash(img2)
    
        distancia = hash1 - hash2
        similitud = 100 - distancia * 100 / 64
        similitud = str(similitud)+" %"
    except Exception as e:
        print("No se pudo calcular el hash, imagen demasiado corrompida.", e)
        similitud = "No dimencionable por hash"
    
    
    print(f"similitud: {similitud}")
    
    
    #Enviar mensaje a la página web por websockets
    return {
        "original": original_b64,
        "comprimida": comprimido_b64,
        "recuperada": recuperada_b64,
        "tam_original": round(tam_original / 1024, 2),
        "tam_comprimido": round(tam_comprimido / 1024, 2),
        "reduccion": round(reduccion, 2),
        "formato": formato,
        "tramasOriginalEnHamming": tramasOriginalEnHamming,
        "tramasCorrompidaEnHamming": tramasCorrompidaEnHamming,
        "posicionesErrores": posicionesErrores,
        "simbolosRecuperados": simbolosRecuperados,
        "simbolosCorrompidos": simbolosCorrompidos,
        "bitsDeError": bitsDeError,
        "similitud": similitud
    }

def comprimir_imagen_local(path, ruido, formato, posicion, distribucionErrores, cantidadErrores):
    #Imagen original
    with open(path, "rb") as f:
        original_bytes = f.read()
    
    original_b64 = base64.b64encode(
        original_bytes
    ).decode()
    
    #Imagen comprimida
    imagen = Image.open(path)
    buffer = io.BytesIO()
    imagen.convert("RGB").save(
        buffer,
        format=formato,
        quality=60
    )
    comprimido_bytes = buffer.getvalue()

    comprimido_b64 = base64.b64encode(
        comprimido_bytes
    ).decode()

    return comprimir_imagen(original_b64, comprimido_b64, original_bytes, comprimido_bytes, ruido, formato, posicion, distribucionErrores, cantidadErrores)
    

def comprimir_imagen_externa(original_b64, ruido, formato, posicion, distribucionErrores, cantidadErrores):
    #Imagen comprimida
    img_bytes = base64.b64decode(original_b64)
    imagen = Image.open(io.BytesIO(img_bytes))
    buffer = io.BytesIO()
    imagen.convert("RGB").save(
        buffer,
        format=formato,
        quality=60
    )
    comprimido_bytes = buffer.getvalue()

    comprimido_b64 = base64.b64encode(
        comprimido_bytes
    ).decode()

    return comprimir_imagen(original_b64, comprimido_b64, img_bytes, comprimido_bytes, ruido, formato, posicion, distribucionErrores, cantidadErrores)
    

def corromper(comprimido_b64, posicion, distribucionErrores, cantidadErrores):
    global tramasOriginalEnHamming
    global tramasCorrompidaEnHamming
    global posicionesErrores
    global simbolosCorrompidos
    global bitsDeError
    tramasOriginalEnHamming = []
    tramasCorrompidaEnHamming = []
    posicionesErrores = []
    simbolosCorrompidos = []
    bitsDeError = []
    posicionInicial = int(len(comprimido_b64)*posicion/100)
    print(f"Posicion inicial del error: {posicionInicial}")
    print(f"Long del comprimido en b64: {len(comprimido_b64)}")
    pasoError = int((len(comprimido_b64)-posicionInicial)/cantidadErrores)
    pasoError = int(distribucionErrores*(pasoError/100))
    print(f"Paso de incerción de error: {pasoError}")
    posicion = posicionInicial
    #caracteres = string.ascii_letters + string.digits
    print(f"{"N° error":<12} | {"Posición":<12} | {"Caracter original":<20} | {"Caracter modificado":<20}")
    for i in range(cantidadErrores):
        if posicion>=1 and posicion<len(comprimido_b64):
            caracterOriginal = comprimido_b64[posicion:posicion+1]
            comprimido_b64 = comprimido_b64[:posicion] + corromperBitEnSimbolo(caracterOriginal) + comprimido_b64[posicion+1:]
            print(f"{i+1:<12} | {posicion:<12} | {caracterOriginal:<20} | {comprimido_b64[posicion:posicion+1]:<20}")
            posicionesErrores.append(posicion)
            simbolosCorrompidos.append(comprimido_b64[posicion:posicion+1])
            posicion = posicion + pasoError
    return comprimido_b64

def corromperBitEnSimbolo(caracterOriginal):
    global bitsDeError
    BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    valor = BASE64_CHARS.index(caracterOriginal)
    bit = random.randint(0, 5)
    bitsDeError.append(f"bit dato {bit+1}")
    valorModificado = valor ^ (1 << bit)
    caracterModificado = BASE64_CHARS[valorModificado]
    agregarTramasEnHamming(valor, valorModificado)
    return caracterModificado

def agregarTramasEnHamming(bitsDatoOriginales, bitsDatoCorrompidos):
    global tramasOriginalEnHamming
    global tramasCorrompidaEnHamming
    #Armado de trama Hamming para 6 bits (b64), paridad PAR:
    #b64: B6, B5, B4, B3, B2, B1
    # 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 | => posiciones
    # R1 | R2 | B1 | R3 | B2 | B3 | B4 | R4 | B5 | B6 | => bits
    # R1: {B1, B2, B4, B5}
    # R2: {B1, B3, B4, B6}
    # R3: {B2, B3, B4}
    # R4: {B5, B6}
    b1 = (bitsDatoOriginales >> 0) & 1;
    b2 = (bitsDatoOriginales >> 1) & 1;
    b3 = (bitsDatoOriginales >> 2) & 1;
    b4 = (bitsDatoOriginales >> 3) & 1;
    b5 = (bitsDatoOriginales >> 4) & 1;
    b6 = (bitsDatoOriginales >> 5) & 1;
    r1 = (b1+b2+b4+b5) & 1;
    r2 = (b1+b3+b4+b6) & 1;
    r3 = (b2+b3+b4) & 1;
    r4 = (b5+b6) & 1;
    tramaOriginal = f"{r1}{r2}{b1}{r3}{b2}{b3}{b4}{r4}{b5}{b6}"
    #print(tramaOriginal)
    
    #c -> bit de dato corrompido
    c1 = (bitsDatoCorrompidos >> 0) & 1;
    c2 = (bitsDatoCorrompidos >> 1) & 1;
    c3 = (bitsDatoCorrompidos >> 2) & 1;
    c4 = (bitsDatoCorrompidos >> 3) & 1;
    c5 = (bitsDatoCorrompidos >> 4) & 1;
    c6 = (bitsDatoCorrompidos >> 5) & 1;
    tramaCorrompida = f"{r1}{r2}{c1}{r3}{c2}{c3}{c4}{r4}{c5}{c6}"
    #print(tramaCorrompida)
    tramasOriginalEnHamming.append(tramaOriginal)
    tramasCorrompidaEnHamming.append(tramaCorrompida)

#Recuperar datos originales con trama Hamming
def recuperarSimbolos():
    global tramasOriginalEnHamming
    global tramasCorrompidaEnHamming
    global simbolosRecuperados
    simbolosRecuperados = []
    BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    print("\nRecuperación de error por Hamming:")
    print(f"{"Trama orig.":<11} | {"Trama corrom.":<13} | {"Pos. error":<10} | Caracter recuperado")
    for i in range(len(tramasCorrompidaEnHamming)):
        trama = int(tramasCorrompidaEnHamming[i], 2)
        #b64: B6, B5, B4, B3, B2, B1
        # 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  | 9  | 10 | => posiciones
        # R1 | R2 | B1 | R3 | B2 | B3 | B4 | R4 | B5 | B6 | => bits
        # R1: {B1, B2, B4, B5}
        # R2: {B1, B3, B4, B6}
        # R3: {B2, B3, B4}
        # R4: {B5, B6}
        r1 = (trama >> 9) & 1;
        r2 = (trama >> 8) & 1;
        b1 = (trama >> 7) & 1;
        r3 = (trama >> 6) & 1;
        b2 = (trama >> 5) & 1;
        b3 = (trama >> 4) & 1;
        b4 = (trama >> 3) & 1;
        r4 = (trama >> 2) & 1;
        b5 = (trama >> 1) & 1;
        b6 = (trama >> 0) & 1;
        r1_calculado = (b1+b2+b4+b5) & 1;
        r2_calculado = (b1+b3+b4+b6) & 1;
        r3_calculado = (b2+b3+b4) & 1;
        r4_calculado = (b5+b6) & 1;
        posicion_error = 0
        if r1_calculado != r1:
            posicion_error = posicion_error + 1
        if r2_calculado != r2:
            posicion_error = posicion_error + 2
        if r3_calculado != r3:
            posicion_error = posicion_error + 4
        if r4_calculado != r4:
            posicion_error = posicion_error + 8
        tramaCorregida = trama ^ ( 1 << (10-posicion_error) )
        b1 = (tramaCorregida >> 7) & 1;
        b2 = (tramaCorregida >> 5) & 1;
        b3 = (tramaCorregida >> 4) & 1;
        b4 = (tramaCorregida >> 3) & 1;
        b5 = (tramaCorregida >> 1) & 1;
        b6 = (tramaCorregida >> 0) & 1;
        bitsDatoCorregido = (b1<<0) + (b2<<1) + (b3<<2) + (b4<<3) + (b5<<4) + (b6<<5)
        simboloCorregido = BASE64_CHARS[bitsDatoCorregido]
        simbolosRecuperados.append(simboloCorregido)
        print(f"{tramasOriginalEnHamming[i]:<11} | {tramasCorrompidaEnHamming[i]:<13} | {posicion_error:<10} | {simboloCorregido:<14}")


def recuperarImagenCorrompida(corrompido_b64):
    recuperarSimbolos()
    for i in range(len(posicionesErrores)):
        posicion = posicionesErrores[i]
        if posicion>=1 and posicion<len(corrompido_b64):
            simboloRecuperado = simbolosRecuperados[i]
            corrompido_b64 = corrompido_b64[:posicion] + simboloRecuperado + corrompido_b64[posicion+1:]
    return corrompido_b64


# websockets
async def handler(ws):
    async for mensaje in ws:
        #Leer mensaje
        data = json.loads(mensaje)
        
        #Imagen solicitada
        if data["origen"] == "precargada":
            nombre              = data["imagen"]
            ruido               = data["ruido"]
            formato             = data["formato"]
            posicion            = data["posicion"]
            distribucionErrores = data["distribucionErrores"]
            cantidadErrores     = data["cantidadErrores"]
            
            print(f"cantidadErrores: {cantidadErrores}")
            print(f"distribucionErrores: {distribucionErrores}")
            print(f"posicion: {posicion}")
            print(f"ruido: {ruido}")
            print(f"nombre: {nombre}")
            
            try:
                posicion = int(posicion)
                distribucionErrores = int(distribucionErrores)
                cantidadErrores = int(cantidadErrores)
            except:
                posicion = 20
                distribucionErrores = 1
                cantidadErrores = 10
            
            path = os.path.join(
                "imagenes",
                f"{nombre}.png"
            )
            
            #Enviar imagenes y parametros de compresión
            resultado = comprimir_imagen_local(path, ruido, formato, posicion, distribucionErrores, cantidadErrores)
            await ws.send(
                json.dumps(resultado)
            )
            
        if data["origen"] == "draged":
            imagen_b64          = data["imagen"]
            ruido               = data["ruido"]
            formato             = data["formato"]
            posicion            = data["posicion"]
            distribucionErrores = data["distribucionErrores"]
            cantidadErrores     = data["cantidadErrores"]
            
            imagen_bytes = base64.b64decode(imagen_b64)
            imagen = Image.open(
                io.BytesIO(imagen_bytes)
            )
            
            print(f"cantidadErrores: {cantidadErrores}")
            print(f"distribucionErrores: {distribucionErrores}")
            print(f"posicion: {posicion}")
            print(f"ruido: {ruido}")
            print(f"nombre: {nombre}")
            
            try:
                posicion = int(posicion)
                distribucionErrores = int(distribucionErrores)
                cantidadErrores = int(cantidadErrores)
            except:
                posicion = 20
                distribucionErrores = 1
                cantidadErrores = 10
            
            resultado = comprimir_imagen_externa(imagen_b64, ruido, formato, posicion, distribucionErrores, cantidadErrores)
            
            await ws.send(
                json.dumps(resultado)
            )

async def websocket_server():
    async with websockets.serve(handler, "localhost", 8765):
        print("ws://localhost:8765")
        await asyncio.Future()


# main del python
if __name__ == "__main__":

    threading.Thread(
        target=iniciar_http,
        daemon=True
    ).start()

    asyncio.run(
        websocket_server()
    )