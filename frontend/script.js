//Script para recepción de imágenes por web socket y mostrarlas en la página web

//Conectarse con el servidor (mismo puerto que el definido en el archivo de python)
const ws = new WebSocket(
    "ws://localhost:8765"
);

ws.onmessage = (event)=>{
	//Leer mensaje recibido
    const data = JSON.parse(event.data);
	
	//Mostrar imagenes
    document.getElementById("original").src = "data:image/png;base64," + data.original;
    document.getElementById("comprimida").src = "data:image/jpeg;base64," + data.comprimida;
	
	//Mostrar metricas de compresión
    document.getElementById("kB_Original").innerHTML = data.tam_original + " kB";
    document.getElementById("kB_Comprimido").innerHTML = data.tam_comprimido + " kB";
    document.getElementById("reduccion").innerHTML = data.reduccion + " %";
};

function solicitarImagen(){
    ws.send(
        JSON.stringify({
            imagen:
            document.getElementById(
                "selector"
            ).value,

            ruido:
            document.getElementById(
                "ruido"
            ).checked
        })
    );
}

//Agregar listener al selector de imagen para pedir al servidor tras selección
document.getElementById("selector").addEventListener("change",solicitarImagen);
document.getElementById("ruido").addEventListener("change",solicitarImagen);

//Pedir imagenes apenas se pueda conectar (para que arranque mostrando imagen1 por defecto)
ws.onopen = solicitarImagen;