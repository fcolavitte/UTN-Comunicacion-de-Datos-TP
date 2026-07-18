# 📚TP grupal - Comunicación de Datos - Ing. en Sistemas
### Grupo 11

### UTN-Comunicacion-de-Datos-TP
Trabajo práctico grupal para la materia Comunicación de Datos de 3er año de la carrera de Ing. en Sistemas de Información de la UTN frlp.

## Integrantes

| Nombre              | GitHub                          | Email                                         |
|---------------------|---------------------------------|-----------------------------------------------|
| Facundo Colavitte   | [@fcolavitte](https://github.com/fcolavitte)     | facundocolavitte@gmail.com   |
| Santiago Ortiz      | [@santiago-sjo](https://github.com/santiago-sjo) | ortizsantiago3010@gmail.com  |
| Martina Ulloa       | [@martiiU](https://github.com/martiiU)           | martinaflorulloa@gmail.com   |
| Franco Kopach       | [@francokoop](https://github.com/francokoop)     | francokoop@gmail.com         |

---

## Estructura del Repositorio

```
postgrado-[equipo]/
├── README.md                   ← Archivo actual
├── main.py                     ← Servidor local en python, se debe ejecutar para que el sistema funcione
│
├── frontend/
│   ├── index.html              ← Página web pricnipal
│   ├── script.js               ← Comunicación con el servidor
│   ├── styles.css              ← Estilos visuales
│   └── icono-utn.png           ← Icono de la UTN para pestaña de la página
│
└── imagenes/                   ← Imagenes para mostrar en la web
```

---

## Dependencias
Se debe instalar:

PIL:<br/>
pip install Pillow

websockets:<br/>
pip install websockets

imagehash:<br/>
pip install ImageHash

---

## Instrucciones de uso

1. Abrir una terminal en la carpeta del proyecto.
2. Ejecutar el archivo principal con:

```bash
python main.py
```

3. Una vez iniciado el servidor, abrir el navegador y entrar a:

```text
http://localhost:8000
```

4. Dejar la terminal abierta mientras se usa la aplicación.
