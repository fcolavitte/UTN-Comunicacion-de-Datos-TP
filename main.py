import asyncio
import json
import base64
import io
import os
import threading

#Para menejo de imágenes
from PIL import Image

#Para comunicación con la página web
import websockets

#Para hostear página index.html en localhost
from http.server import HTTPServer, SimpleHTTPRequestHandler


# HTTP index
class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)

def iniciar_http():
    servidor = HTTPServer(("localhost", 8000), FrontendHandler)
    print("http://localhost:8000")
    servidor.serve_forever()



# Compresión
def comprimir_jpeg(path):
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
        format="JPEG",  #Cambiar "JPEG" acá para tipo de reducción, por defecto Pillow admite JPEG, cargar otras librerías
        quality=60
    )
    comprimido_bytes = buffer.getvalue()

    comprimido_b64 = base64.b64encode(
        comprimido_bytes
    ).decode()

    
    #Meter ruido en la comunicación (modificar bytes de la foto comprimida)
    print(comprimido_b64)
    print()
    print()
    print(comprimido_b64[1010:1021])
    comprimido_b64 = comprimido_b64[:1010] + "iigAooooAKo" + comprimido_b64[1021:] #Original en el gato: iigAooooAKK
    print(comprimido_b64[1010:1021])
    #Fin ruido

    tam_original = len(original_bytes)
    tam_comprimido = len(comprimido_bytes)

    reduccion = ( 100 - (tam_comprimido * 100 / tam_original) )
    
    #Enviar mensaje a la página web por websockets
    return {
        "original": original_b64,
        "comprimida": comprimido_b64,
        "tam_original": round(tam_original / 1024, 2),
        "tam_comprimido": round(tam_comprimido / 1024, 2),
        "reduccion": round(reduccion, 2),
        "formato": "JPEG"
    }



# websockets
async def handler(ws):
    async for mensaje in ws:
        #Leer mensaje
        data = json.loads(mensaje)
        
        #Imagen solicitada
        nombre = data["imagen"]
        path = os.path.join(
            "imagenes",
            f"{nombre}.png"
        )
        
        #Enviar imagenes y parametros de compresión
        resultado = comprimir_jpeg(path)
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