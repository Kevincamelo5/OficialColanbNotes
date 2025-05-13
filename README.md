# 📘 ColabNotes

**ColabNotes** es una aplicación web enfocada en facilitar la colaboración entre alumnos a través de un foro académico. Los estudiantes pueden registrarse utilizando su correo institucional y una contraseña segura, interactuar con otros compañeros, crear notas y apoyarse mutuamente en sus estudios.

---

# 🧑‍🤝‍🧑 integrantes

- Kevin Leandro Camelo Suaste.
- Roger Aguila Uicab.
- Miguel Angel Gomez Hergera.
- Diego Alexander Rosado Valle.
---

## 🚀 Características principales

- Registro y autenticación de usuarios mediante correo institucional.
- Interfaz tipo foro para la comunicación entre alumnos.
- Creación, visualización y organización de notas.
- Sistema de apoyo académico entre compañeros.

---

## 🛠️ Tecnologías utilizadas

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)

---

 ## Vistas de la interfaz de usuario

- ![Vista del inicio de sesion](imagenes/inicioDeSesion.jpg)
  *Vista del inicio de sesión del usuario.*
- ![Vista registro de usuario](imagenes/RegistroUsario.jpg)
  *Vista deñ registro de Usuario*
- ![Vista del menu principal del usuario](imagenes/VistaPrincipal.jpg)
*Vista del menú principal* 
- ![Vista de todas las notas generadas](imagenes/PrimeraVistaDeNotas.jpg)
*Vista previa de las notas personales del usuario* 
- ![vista detallada de la nota](imagenes/VistaDetalladaDeLaNota.jpg)
*Vista detallada de una nota especifica* 
- ![Vista de la edicion de la nota](imagenes/EdicionDeLaNota.jpg)
*Vista de la edición de la nota generada* 
- ![Vista general de los foros guardados](imagenes/VistaForos.jpg)
*Vista previa de los foros a los que esta inscrito el usuario* 
- ![Vista espececifica de la conversación dentro del foro](imagenes/VistaDentroForo.jpg)
*Vista de una conversación de un foro* 
- ![Vista general de la busqueda de foros para suscribirse](imagenes/VistaBuscarForos.jpg)
*Vista previa de la busqueda de foros a los que el usuario no esta inscrito* 
- ![Vista especifica de una conversación privada con un usuario de prueba](imagenes/VistaChatPrivado.jpg)
*Vista dentro de una conversación privada con un usuario de prueba* 
- ![Vista general de la busqueda de contactos y la aceptación de solicitudes de amistad](imagenes/VistaBuscarYAceptarContactos.jpg)
*Vista previa de la busqueda de usuarios y recepción de solicitudes de amistad* 

---

## ⚙️ Instalación y ejecución

Sigue los pasos a continuación para ejecutar el proyecto localmente:

1. Abre tu terminal y navega a la carpeta principal del proyecto:
   ```bash
   cd ColabNotes

2. Crea un entorno virtual:
    ```bash
    python -m venv venv

3. Activa el entorno virtual:

    En Windows:
    ```bash
    venv\Scripts\activate

    En macOS/Linux:
    ```bash
    source venv/bin/activate

4. Instala las dependencias requeridas:

    ```bash
    pip install flask flask_sqlalchemy flask_login

5. Crea la base de datos (solo si no existe):

    ```bash
    python create_db.py

7. Ejecuta la aplicación:

    ```bash
    python run.py

    
La aplicación estará disponible en http://localhost:5000.
