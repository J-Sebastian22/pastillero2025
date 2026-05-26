# API Pillbox — Backend

Backend del sistema **Pastillero Inteligente 2025**. Expone una API REST que
permite gestionar usuarios, medicamentos, horarios de tomas, dispositivos
físicos (ESP32), contactos de emergencia, registros de toma y notificaciones.

---

## 1. Descripción a alto nivel

`api_pillbox` es el componente servidor de la solución *Pastillero 2025*. Su
objetivo es controlar y registrar la adherencia al tratamiento de un paciente
mediante un dispositivo IoT (ESP32) que entrega medicamentos a horas
programadas. El backend se encarga de:

- **Gestión de cuentas**: registro y autenticación básica de usuarios por
  correo y contraseña.
- **Catálogo de medicamentos**: cada usuario puede crear sus propios
  medicamentos con nombre, descripción y dosis.
- **Programación de tomas**: cada medicamento puede tener uno o varios
  horarios, definidos por una hora base y una frecuencia (en horas) que
  determina cada cuánto debe repetirse la toma.
- **Cálculo automático de próximas tomas**: el modelo `Horario` expone una
  propiedad `proxima_toma` que calcula, según la zona horaria
  `America/Bogota`, el próximo `datetime` en el que debería entregarse el
  medicamento.
- **Vinculación con dispositivos**: cada usuario puede registrar uno o varios
  dispositivos ESP32 (identificados por IP) que serán los responsables físicos
  de dispensar el medicamento.
- **Registro de tomas y notificaciones**: cada toma programada queda
  registrada (hora programada vs. hora real) y puede disparar notificaciones
  hacia los contactos de emergencia del usuario.
- **Endpoint dedicado para el front**: `proximos-horarios` entrega los cinco
  próximos eventos ya calculados, listos para mostrarse en la interfaz
  Angular.

La API se consume desde la SPA en Angular ubicada en `../pillbox-app`. CORS
está abierto únicamente a `http://localhost:4200` y `http://127.0.0.1:4200`
en el entorno de desarrollo.

---

## 2. Tecnologías utilizadas

| Categoría             | Tecnología                            | Versión / Detalle          |
|-----------------------|---------------------------------------|----------------------------|
| Lenguaje              | Python                                | 3.10+ (recomendado 3.11)   |
| Framework web         | Django                                | 5.2.7                      |
| API REST              | Django REST Framework (DRF)           | Última estable             |
| Gestor de BD          | PostgreSQL                            | 13+                        |
| Driver de BD          | psycopg2 / psycopg2-binary            | 2.9+                       |
| CORS                  | django-cors-headers                   | Última estable             |
| Servidor de desarrollo| `runserver` (Django)                  | Incluido                   |
| Zona horaria          | `America/Bogota` (`USE_TZ = True`)    | Configurada en settings    |
| Frontend consumidor   | Angular (proyecto `pillbox-app`)      | Servido en :4200           |
| Hardware              | ESP32 (cliente HTTP que consulta API) | Externo                    |

### Plugins / dependencias de Django

Instaladas en `INSTALLED_APPS` (`api_pillbox/settings.py`):

- `corsheaders` — permite peticiones cruzadas desde el front Angular.
- `rest_framework` — provee los `ViewSet`, `Serializer`, `Router` y
  decoradores `@api_view` utilizados en la API.
- `core` — aplicación propia del proyecto que contiene modelos, serializers
  y vistas.

> **Nota:** este repositorio no incluye un `requirements.txt`. La sección de
> instalación más abajo detalla cómo generarlo o instalar las dependencias
> manualmente.

---

## 3. Estructura del proyecto

```
api_pillbox/
├── manage.py                # Punto de entrada CLI de Django
├── api_pillbox/             # Configuración del proyecto
│   ├── settings.py          # Configuración (BD, CORS, apps, zona horaria)
│   ├── urls.py              # Enrutador raíz + DRF DefaultRouter
│   ├── wsgi.py / asgi.py    # Entradas para servidores WSGI/ASGI
└── core/                    # Aplicación de negocio
    ├── models.py            # Usuario, Contacto, Dispositivo, Medicamento,
    │                         #   Horario, Registro_Toma, Notificacion
    ├── serializers.py       # Serializers DRF de los modelos
    ├── views.py             # ViewSets + funciones registrar/login/proximos
    ├── admin.py             # (Sin modelos registrados)
    ├── apps.py              # Configuración de la app
    └── migrations/          # Migraciones generadas por Django
```

---

## 4. Requisitos previos

Antes de instalar el backend asegúrate de tener:

1. **Python 3.10 o superior** disponible en el `PATH`.
2. **PostgreSQL 13 o superior** instalado, en ejecución y accesible en
   `localhost:5432`.
3. **pip** y, opcionalmente, **virtualenv** o el módulo nativo `venv`.
4. Acceso de administrador a PostgreSQL para crear la base de datos.

---

## 5. Guía de instalación

A continuación se describe el proceso completo paso a paso en Windows
(PowerShell). Para Linux/macOS los comandos equivalentes están entre
paréntesis cuando difieren.

### 5.1 Clonar el repositorio

```powershell
git clone <url-del-repositorio> pastillero2025
cd pastillero2025\api_pillbox
```

### 5.2 Crear y activar el entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate
```

### 5.3 Instalar dependencias

Como el proyecto aún no tiene `requirements.txt`, instala los paquetes
directamente:

```powershell
pip install --upgrade pip
pip install "Django==5.2.7" djangorestframework django-cors-headers psycopg2-binary
```

Recomendado: una vez instaladas, congela las versiones para reproducibilidad:

```powershell
pip freeze > requirements.txt
```

### 5.4 Crear la base de datos en PostgreSQL

Conéctate a `psql` con el usuario `postgres` y crea la base de datos:

```sql
CREATE DATABASE pillbox_db;
```

> Las credenciales por defecto definidas en `settings.py` son:
> - **NAME**: `pillbox_db`
> - **USER**: `postgres`
> - **PASSWORD**: `0000`
> - **HOST**: `localhost`
> - **PORT**: `5432`
>
> Si tu entorno usa otras credenciales, edita
> `api_pillbox/api_pillbox/settings.py` antes de continuar.

### 5.5 Aplicar las migraciones

```powershell
python manage.py migrate
```

Esto creará todas las tablas necesarias (`core_usuario`, `core_contacto`,
`core_dispositivo`, `core_medicamento`, `core_horario`,
`core_registro_toma`, `core_notificacion`) además de las tablas internas
de Django.

### 5.6 (Opcional) Crear superusuario para el admin

```powershell
python manage.py createsuperuser
```

Con esto podrás ingresar al panel administrativo en
`http://127.0.0.1:8000/admin/`.

---

## 6. Ejecución

### 6.1 Arrancar el servidor de desarrollo

Desde la carpeta `api_pillbox/` (donde está `manage.py`):

```powershell
python manage.py runserver
```

Por defecto el servidor queda escuchando en
`http://127.0.0.1:8000/`.

Para exponerlo en la red local (útil si el ESP32 está en otra máquina):

```powershell
python manage.py runserver 0.0.0.0:8000
```

> Si lo haces, recuerda agregar la IP a `ALLOWED_HOSTS` dentro de
> `settings.py` (actualmente está vacío y solo funciona con `DEBUG=True`).

### 6.2 Verificar que la API responde

Con el servidor corriendo, en otra terminal:

```powershell
curl http://127.0.0.1:8000/api/usuarios/
```

Debe devolver `[]` (lista vacía) si aún no hay usuarios, o un JSON con la
lista existente.

### 6.3 Endpoints raíz disponibles

- **Admin Django**: `http://127.0.0.1:8000/admin/`
- **API REST**: `http://127.0.0.1:8000/api/`
  - `usuarios/`, `contactos/`, `dispositivos/`, `medicamentos/`,
    `horarios/`, `registros/`, `notificaciones/`
  - `registro/` (POST, alta de usuario)
  - `login/` (POST, autenticación)
  - `proximos-horarios/?id_usuario=<id>` (GET, próximos 5 horarios)

Para el detalle completo de cada endpoint consulta
[`README_ENDPOINTS.md`](./README_ENDPOINTS.md). Para el modelo de datos y
diccionario de tablas consulta
[`README_DICCIONARIO_DATOS.md`](./README_DICCIONARIO_DATOS.md). Para probar
todo desde Postman importa el archivo
[`api_pillbox.postman_collection.json`](./api_pillbox.postman_collection.json).

---

## 7. Notas de seguridad y producción

- El `SECRET_KEY` está embebido en `settings.py` y debe rotarse antes de
  publicar el servicio.
- `DEBUG = True` y `ALLOWED_HOSTS = []` son válidos solo para desarrollo.
- Las contraseñas de usuario se guardan en texto plano en la tabla
  `core_usuario`. **No usar este backend en producción sin migrar a hash
  (`make_password` / `check_password`) y a tokens/JWT para la autenticación.**
- El CORS está limitado al puerto 4200 (Angular). Ajusta
  `CORS_ALLOWED_ORIGINS` si despliegas el front en otra URL.

---

## 8. Solución de problemas comunes

| Problema                                                | Causa probable                                              | Acción sugerida                                                                 |
|---------------------------------------------------------|-------------------------------------------------------------|---------------------------------------------------------------------------------|
| `django.db.utils.OperationalError: could not connect...`| PostgreSQL apagado o credenciales incorrectas               | Verifica que el servicio esté arriba y ajusta `DATABASES` en `settings.py`.    |
| `ModuleNotFoundError: No module named 'corsheaders'`    | Falta instalar `django-cors-headers`                        | `pip install django-cors-headers`                                              |
| `CORS error` en el navegador                            | El front está en un origen distinto a los permitidos         | Agrega el origen a `CORS_ALLOWED_ORIGINS`.                                     |
| `proxima_toma` devuelve siempre el mismo valor          | `frecuencia = 0` en el horario                              | Define una frecuencia mayor a 0 en el `Horario` correspondiente.               |
| Error `relation "core_usuario" does not exist`          | No se ejecutaron las migraciones                            | Ejecuta `python manage.py migrate`.                                            |
