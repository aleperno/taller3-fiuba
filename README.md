# Proyecto para Taller de Programación 3 - FIUBA - Cátedra Mendez
# FIUBA Apuntes

El proyecto está inspirado en la difusión de apuntes entre alumnos de la facultad. No le es ajeno a nadie la gran
cantidad de apuntes que se distribuyen de manera organica entre alumnos en la facultad. Sin embargo encontramos dos
grandes problemáticas

## Video Demo

Una demo del proyecto puede verse [acá](https://youtu.be/VmTowG-jWfw)

# Introducción

1. **Centralización**: No existe hoy una única fuente donde se puedan encontrar o buscar los apuntes. Hoy los recursos
   están distribuidos en grupos de Facebook, Drive, Github, etc. El objetivo sería centralizar todos estos recursos en
   un único lugar, done los alumnos puedan subir, categorizar, compartir, buscar y descargar apuntes.
2. **Calidad**: La calidad de los apuntes es muy variable, si bien las cámaras de los celulares hoy en día poseen gran
   definición, no es raro encontrase con apuntes cuya fuente son fotos carentes de nitidez. También sucede que archivos
   que sí poseen buena definición, tambien poseen un gran tamaño lo que dificulta su veloz descarga. El objetivo de este
   item es otorgar herramientas de procesamiento de imagen para mejorar la calidad de las imágenes, a la vez de lograr
   tamaños de archivos manejables.
3. **Digitalización**: La mayoría de los apuntes siguen siendo en formato papel con letra manuscrita, una de las herramientas
   que proveeremos será la capacidad de convertir estos apuntes a PDF mediante LaTeX, así como proveer las fuentes de
   LaTeX para que los alumnos puedan editar los apuntes a su gusto.


# Funcionalidades

A continuación describiremos las funcionalidades actualmente presentes en la aplicación

- **Login**: El login se realiza mediante Single Sign-On con una cuenta de Google, esto se decidió dado que hoy en día la
  mayoría cuenta con una cuenta `@fi.uba.ar`. Este feature se implementó mediante el uso de Firebase, lo que también
  facilita la implementación de otros medios de login.

- **Subida de apuntes**: Los usuarios pueden subir sus apuntes, al momento de seleccionar el archivo a subir (que como
  restricción debe ser un archivo PDF), se mostrará el archivo seleccionado a la izquierda y a la derecha se mostrará
  un menú con las siguientes opciones
  - **Nombre**: Por defecto toma el nombre del archivo subido, el usuario puede modificarlo.
  - **Comprimir**: Existe la posibilidad de comprimir el archivo, de seleccionar esta alternativa se mostrarán opciones
    adicionales
    - **Colores**: Define el número de colores que tendrá el archivo final.
    - **Fondo en Blanco**: Si se selecciona esta opción, se intentará detectar el fondo de los archivos y se reemplazará
      por blanco.
  - **Privacidad**: El usuario puede seleccionar la privacidad del archivo, puede ser público, privado o restringido.
    - **Público**: Cualquier usuario puede ver y descargar el archivo.
    - **Privado**: Solo el usuario que subió el archivo puede verlo y descargarlo.
    - **Restringido**: El usuario deberá ingresar las cuentas de email de quienes quiere que puedan tener acceso al
      archivo
  - **Convertir a Latex**: De seleccionar esta opción el archivo se procesará mediante un convertidor de latex, dando
    como resultado un `.zip` con las fuentes de LaTeX y el archivo PDF.

- **Tareas en Progreso**: Se muestra un listado de las tareas del usuario que se están realizando en el servidor, 
  por ejemplo compresión de archivos, conversión a LaTeX, etc.

- **Apuntes**: Se muestra los apuntes subidos por el usuario, con cada uno de los links disponibles a los recursos
- **Compartidos**: Se muestran los apuntos ajenos a los cual tiene acceso el usuario

# Arquitectura y Tecnologías

## Frontend

El frontend fue desarrollado en React con Typescript y se hace un gran uso de React-Bootstrap. Para el login se emplea
el servicio de FireBase.

## Backend

El backend está compuesto por diversos componentes

### API
La API que sirve al frontend, está desarrollada en Python con FastAPI.

### Worker
El backend asímismo posee un worker que se encarga de procesar tareas, a excepción de la tarea de compresión. Como 
tecnologías principales se emplea Celery + RabbitMQ para las tareas y SQLAlchemy + PostgreSQL para la base de datos.

### Beat
Existe una tarea que debe ejecutarse periodicamente, que se encargará de actualizar el estado de la conversión a latex
que es hecha por un servicio externo. Para esto se emplea un worker especifico que correra un Celery Beat.

## Almacenamiento de Archivos
Para el almacenamiento de archivos empleamos un FTP de un dominio que ya poseiamos, sin embargo alguna solución más
elegante podría ser emplear algun servicio Cloud como AWS S3.

## Workers de Compresión

Dentro del dominio de nuestro problema, la parte mas intensiva es la de compresión de los archivos, el cuál se hace
página por página mediante procesamiento de imágenes empleado la libreria [noteshrink](https://github.com/mzucker/noteshrink).
Para esto se emplea un worker específico, fácilmente escalable, que se encargará de realizar la compresión de las
páginas y devolver el resultado.

## Latex Builder

El servicio externo que empleamos para la conversión a LaTeX nos provee un .zip con las fuentes pero no nos provee el
PDF; es por ello que tenemos una instancia aparte la cuál ejecutará las tareas de buildear el PDF a partir de las fuentas.


## Conversión a Latex

Uno de los puntos más interesantes de este proyecto es el de poder convertir apuntes manuscritos a LaTeX. Para esto
hacemos uso del servicio de [Mathpix](https://mathpix.com/), el cuál nos provee una API para realizar la conversión de
archivos a LaTeX. El servicio es de gran calidad, sin embargo es pago. Se evaluaron diversas alternativas open-source,
logrando resultados pobres y cuyo trabajo adicional escapaba al alcance del proyecto. Algunas de las pruebas pueden
verse [acá](https://github.com/aleperno/taller3-fiuba/tree/main/ocr_tests)

> **IMPORTANTE**: Los archivos se pasan mediante una URL a Mathpix, por lo que de querer correr este proyecto 100% local
> con un FTP local, es un punto a tener en cuenta


## Firebase
Para ejecutar localmente la plataforma empleamos un servicio de emulacion de Firebase. La imagen de Docker que empleamos
la basamos en el siguiente [proyecto publico](https://github.com/grodin/firebase-emulator-docker)


# Despliegue

El proyecto se encuentra 100% containerizado, por lo que el despliegue es sencillo.
```
docker compose up
```

## Pre-requisitos
Siendo que se emplean servicios externos como el servidor FTP y Mathpix, es necesario definir las credenciales para
cada uno de ellos.
En el proyecto se provee un archivo `.env.example` que deberá ser renombrado a `.env` y completado con las credenciales
pertinentes.

Asímismo en la carpeta `frontend` se encuentra un archivo `firebaserc` que es necesario modificar para que el nombre del
proyecto de firebase sea el correcto

# Próximos Pasos y Posibles Mejoras

Consideramos que si bien el estado del proyecto es el de una versión MVP, sienta una sólida base para futuros proyectos,
aquí se van a definir potenciales mejoras desde lo técnico hasta lo funcional.


## Mejoras Técnicas
- Tests: Agregar tests y CI/CD para hacer el proyecto mas robusto y resiliente acorde vaya creciendo
- CDN: Actualmente cualquiera con una URL puede acceder a los archivos, sería interesante implementar una CDN con autenticación
  para evitar esto.
- Websockets: Actualmente todas las vistas poseen un botón para actualizar cierta data, sería bueno emplear websockets
  para que la data se actualice sin intervención del usuario
- Paginado: Implementar paginado en la devolución de los archivos para evitar devolver todo
- Digitalización: Encontrar o implementar una alternativa open-source a Mathpix.
- Chrome: La ventana de subida de archivos no muestra correctamente archivos grandes si nos encontramos en Chrome.
- Firefox: Falla el mecanismo de `Drag-n-Drop` en la pestaña de subida de archivos.


## Mejoras Funcionales
- Calificaciones: Implementar un sistema de puntajes para que los usuarios puedan calificar los apuntes y dejar sus comentarios
- Categorización: Implementar un sistema de categorización para que un usuario pueda definir a que materia pertenece el apunte,
  también se podria permitir categorias mas granulares como materia y tema, etc. Mismo podria ser un sistema de TAGS.
- Cambios a posteriori: Actualmente no se permite realizar cambios una vez subido el archivo, como el nombre, privacidad,
  o elegir comprimirlo si no se eligió en un principio.
- Red Social: Establecer opciones mas opciones para compartir los apuntes, por ejemplo si los usuarios pudisen "agregarse"
  entre sí y definir una serie de grupos; estas podrian ser otras opciones de privacidad de los archivos ('solo mis amigos',
  'grupo llamado xxx').
- Notificaciones: Implementar un sistema de notificaciones para que los usuarios puedan recibir notificaciones de nuevos
  apuntes subidos, cambios en los apuntes compartidos, etc.
- Tokens / Sistema de pago: Siendo que actualmente la conversión a LaTeX es un servicio pago, se podría implementar algún
  mecanismo para solventar dicho costo. Ya sea haciendole abonar al usuario directamente como estableciendo algun sistema
  de tokens que se podrian o comprar o ganar (por ejemplo, por subir apuntes, calificarlos, etc.).
- Auth Token Externo: Otra alternativa al punto anterior sería que el usuario deba ser el que se suscriba al servicio
  de Matpix y le ceda los auth tokens a la aplicación. De esta forma la plataforma empleará las credenciales de los
  usuarios y no una propia.
- Monetización: Implementar un sistema de monetización para que los usuarios puedan vender sus apuntes. No es la opción
  que mas nos guste dado que creemos firmemente en la colaboración entre estudiantes, pero entendemos desde un punto de
  vista de negocio que puede ser interesante.
- Perfil: Permitir cambios en el perfil de usuario, como foto, nombre, etc.
- Borrado y Baja: Permitir al usuario borrar sus apuntes, o darse de baja de la plataforma.


## Mejoras Funcionales y Técnicas
Existen también mejoras que son tanto funcionales como técnicas

 - OCR Colaborativo: Supongamos que se quiere desarrollar un sistema de OCR propio mediante ML, se requieren iteraciones
   de aprendizaje y de validación. Sería interesante implementar un sistema donde los usuarios puedan colaborar con el
   armado del set de aprendizaje como también de validar las iteraciones de la misma. Algunas opciones podrían ser
   - El usuario distingue de un archivo las porciones correspondiente a texto, gráficos o ecuaciones
   - El usuario dado un texto o ecuación, debe ingresar el texto o la ecuación en su formato latex.
   - El usuario debe validar si el resultado devuelto por el sistema es correcto o no.
   
   Estas tareas podrian ser o bien obligatorias para el usuario (quiza otorgandole tokens que serán necesarias para la aplicación),
   o bien voluntarias o para acceder a alguna funcionalidad "premium".

# Integrantes
 - [Alejandro Pernin](https://github.com/aleperno)
 - [Pablo Berrotaran](https://github.com/PBrrtrn)
 - [Luciano Sportelli Castro](https://github.com/sportelliluciano)
