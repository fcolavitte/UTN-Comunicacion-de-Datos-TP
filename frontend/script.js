//Script para recepción de imágenes por web socket y mostrarlas en la página web


//Drag de imagenes
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");


//Conectarse con el servidor (mismo puerto que el definido en el archivo de python)
const ws = new WebSocket(
    "ws://localhost:8765"
);

ws.onmessage = (event)=>{
	//Leer mensaje recibido
    const data = JSON.parse(event.data);
	
	//Mostrar imagenes
    document.getElementById("original").src = "data:image/png;base64," + data.original;
    document.getElementById("comprimida").src = "data:image/" + data.formato.toLowerCase() + ";base64," + data.comprimida;//data.comprimida/recuperada
     
    document.getElementById("textoFormato").innerHTML ="Imagen comprimida (." +data.formato.toLowerCase() + ")";
		
	//Mostrar metricas de compresión
    document.getElementById("kB_Original").innerHTML = data.tam_original + " kB";
    document.getElementById("kB_Comprimido").innerHTML = data.tam_comprimido + " kB";
    document.getElementById("reduccion").innerHTML = data.reduccion + " %";
	
	//Mostrar Parámetros de Error
    document.getElementById("similitud").innerHTML = data.similitud;
	
	//Mostrar imagenes recuperadas
    document.getElementById("corrompida").src = "data:image/png;base64," + data.comprimida;
    document.getElementById("recuperada").src = "data:image/" + data.formato.toLowerCase() + ";base64," + data.recuperada;//data.comprimida/recuperada
	
	const tbody = document.querySelector("#tablaHamming tbody");
	tbody.innerHTML = "";
	for (let i = 0; i < data.bitsDeError.length; i++) {
		agregarPasoHamming(data.posicionesErrores[i], data.tramasCorrompidaEnHamming[i], data.simbolosCorrompidos[i], data.bitsDeError[i], data.tramasOriginalEnHamming[i], data.simbolosRecuperados[i])
	}
	
};

function agregarPasoHamming(num_bloque, trama_recibida, simbolo_recibido, bit_error, trama_corregida, simbolo_corregido){
    const tbody = document.querySelector("#tablaHamming tbody");

    const fila = document.createElement("tr");

    fila.innerHTML = `
        <td>${num_bloque}</td>
        <td>${trama_recibida}</td>
        <td>${simbolo_recibido}</td>
        <td>${bit_error}</td>
        <td>${trama_corregida}</td>
        <td>${simbolo_corregido}</td>
    `;

    tbody.appendChild(fila);
}

function solicitarImagen(){
	if(fileInput.files[0] && document.getElementById("selector").value == "otra"){
		enviarImagen(fileInput.files[0]);
	}else if(document.getElementById("selector").value != "otra"){
		ws.send(
			JSON.stringify({
				origen:
				"precargada",
				imagen:
				document.getElementById(
					"selector"
				).value,
				ruido:
				document.getElementById(
					"ruido"
				).checked,
				posicion:
				document.getElementById(
					"posicion"
				).value,
				distribucionErrores:
				document.getElementById(
					"distribucionErrores"
				).value,
				cantidadErrores:
				document.getElementById(
					"cantidadErrores"
				).value,
				formato:
				document.getElementById(
					"formato"
				).value
			})
		);
	}
}


function cambioSelectorImagen(){
	if(document.getElementById("selector").value == "otra"){
		document.getElementById("dropZone").style.visibility="visible";
	}else{
		solicitarImagen();
		document.getElementById("dropZone").style.visibility="hidden";
		fileInput.value = "";
	}
}

//Agregar listener al selector de imagen para pedir al servidor tras selección
document.getElementById("selector").addEventListener("change",cambioSelectorImagen);
document.getElementById("ruido").addEventListener("change",solicitarImagen);
document.getElementById("formato").addEventListener("change",solicitarImagen);
document.getElementById("posicion").addEventListener("change",solicitarImagen);
document.getElementById("distribucionErrores").addEventListener("change",solicitarImagen);
document.getElementById("cantidadErrores").addEventListener("change",solicitarImagen);


//Pedir imagenes apenas se pueda conectar (para que arranque mostrando imagen1 por defecto)
ws.onopen = solicitarImagen;


//Drag de imagen


browseBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
});

dropZone.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", () => {
    if(fileInput.files.length > 0){
        enviarImagen(fileInput.files[0]);
    }
});

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if(file){
        fileInput.files = e.dataTransfer.files;
        enviarImagen(file);
    }
});

let archivoSeleccionado = null;

function enviarImagen(file){
	console.log(file);
    if (!file) return;
	archivoSeleccionado = file;
	const reader = new FileReader();
    
    reader.onload = function(e) {
        // e.target.result returns "data:image/png;base64,AAAA...."
        const base64 = e.target.result.split(",")[1];
        
        ws.send(JSON.stringify({
            origen: "draged",
            imagen: base64,
            ruido: document.getElementById("ruido").checked,
            posicion: document.getElementById("posicion").value,
            distribucionErrores: document.getElementById("distribucionErrores").value,
            cantidadErrores: document.getElementById("cantidadErrores").value,
            formato: document.getElementById("formato").value
        }));
		
    };

    reader.onerror = function(error) {
        console.error("Error reading file:", error);
    };

    reader.readAsDataURL(file);
	
}



