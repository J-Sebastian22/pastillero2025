# API Pillbox — Documentación de Endpoints

Esta guía describe **módulo por módulo y endpoint por endpoint** la API REST
expuesta por `api_pillbox`. Cada sección incluye:

- Método HTTP, URL y descripción.
- Atributos del cuerpo (request) con tipo y explicación.
- Atributos de la respuesta (response) con tipo y explicación.
- Ejemplos reales de `curl` y de `JSON` listos para ejecutar.
- Posibles respuestas de error.

> **URL base (entorno local):** `http://127.0.0.1:8000`
>
> Todos los endpoints REST (excepto `admin/`) viven bajo el prefijo `/api/`.
>
> El backend **no** utiliza autenticación por token todavía: los endpoints
> son accesibles directamente. La identificación del usuario en operaciones
> que dependen de él (horarios, medicamentos, etc.) se realiza enviando
> `id_usuario` como dato o `query param`.

---

## Índice de módulos

1. [Autenticación](#1-modulo-autenticacion)
2. [Usuarios](#2-modulo-usuarios)
3. [Contactos](#3-modulo-contactos)
4. [Dispositivos](#4-modulo-dispositivos)
5. [Medicamentos](#5-modulo-medicamentos)
6. [Horarios](#6-modulo-horarios)
7. [Registros de toma](#7-modulo-registros-de-toma)
8. [Notificaciones](#8-modulo-notificaciones)
9. [Próximos horarios (dashboard)](#9-modulo-proximos-horarios)
10. [Códigos de error comunes](#10-codigos-de-error-comunes)

---

## 1. Módulo: Autenticación

Aunque comparte tablas con el módulo de usuarios, expone dos endpoints
dedicados al registro y login. **Las contraseñas viajan y se almacenan en
texto plano** en esta versión.

### 1.1 `POST /api/registro/` — Crear un nuevo usuario

Crea un usuario en la base de datos. Es equivalente a `POST /api/usuarios/`
pero está expuesto bajo una URL más descriptiva, pensada para el flujo de
registro desde la app.

**Request body:**

| Campo      | Tipo     | Requerido | Descripción                                          |
|------------|----------|-----------|------------------------------------------------------|
| `nombre`   | string   | Sí        | Nombre completo del usuario (máx. 100 caracteres).  |
| `correo`   | string   | Sí        | Correo electrónico único.                            |
| `password` | string   | Sí        | Contraseña en texto plano (máx. 100 caracteres).    |
| `telefono` | string   | Sí        | Número de teléfono (máx. 15 caracteres).            |
| `activo`   | boolean  | No        | Estado del usuario. Default `true`.                  |

**Respuesta 201 Created:**

```json
{
  "id": 1,
  "nombre": "Cristian Benavides",
  "correo": "cristian@example.com",
  "password": "MiClave123",
  "telefono": "3001234567",
  "activo": true,
  "fecha_creacion": "2026-05-26T10:15:30.123456-05:00"
}
```

**Respuesta 400 Bad Request** (correo duplicado o datos inválidos):

```json
{
  "correo": ["usuario con este correo ya existe."]
}
```

**Ejemplo `curl`:**

```bash
curl -X POST http://127.0.0.1:8000/api/registro/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Cristian Benavides\",\"correo\":\"cristian@example.com\",\"password\":\"MiClave123\",\"telefono\":\"3001234567\"}"
```

---

### 1.2 `POST /api/login/` — Autenticar a un usuario

Valida `correo` y `password`. Si coinciden, devuelve los datos del usuario.

**Request body:**

| Campo      | Tipo   | Requerido | Descripción              |
|------------|--------|-----------|--------------------------|
| `correo`   | string | Sí        | Correo del usuario.      |
| `password` | string | Sí        | Contraseña en texto plano. |

**Respuesta 200 OK:**

```json
{
  "id": 1,
  "nombre": "Cristian Benavides",
  "correo": "cristian@example.com",
  "password": "MiClave123",
  "telefono": "3001234567",
  "activo": true,
  "fecha_creacion": "2026-05-26T10:15:30.123456-05:00"
}
```

**Respuesta 401 Unauthorized:**

```json
{ "error": "Credenciales inválidas" }
```

**Ejemplo `curl`:**

```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d "{\"correo\":\"cristian@example.com\",\"password\":\"MiClave123\"}"
```

---

## 2. Módulo: Usuarios

CRUD completo del recurso **Usuario**. Expuesto vía `ViewSet` de DRF, por lo
que soporta las cinco operaciones estándar.

### Esquema del recurso

| Campo            | Tipo     | Lectura/Escritura | Descripción                                                            |
|------------------|----------|-------------------|------------------------------------------------------------------------|
| `id`             | integer  | Lectura           | Identificador autogenerado.                                            |
| `nombre`         | string   | RW                | Nombre del usuario, máx. 100 caracteres.                               |
| `correo`         | string   | RW                | Correo único.                                                          |
| `password`       | string   | RW                | Contraseña, máx. 100 caracteres.                                       |
| `telefono`       | string   | RW                | Teléfono, máx. 15 caracteres.                                          |
| `activo`         | boolean  | RW                | Si el usuario está habilitado. Default `true`.                         |
| `fecha_creacion` | datetime | Lectura           | Fecha de alta. Se completa al crear con `timezone.now`.                |

### 2.1 `GET /api/usuarios/`

Lista todos los usuarios.

**Respuesta 200 OK:**

```json
[
  {
    "id": 1,
    "nombre": "Cristian Benavides",
    "correo": "cristian@example.com",
    "password": "MiClave123",
    "telefono": "3001234567",
    "activo": true,
    "fecha_creacion": "2026-05-26T10:15:30.123456-05:00"
  }
]
```

```bash
curl http://127.0.0.1:8000/api/usuarios/
```

### 2.2 `POST /api/usuarios/`

Crea un usuario. Mismos campos que `/api/registro/`.

```bash
curl -X POST http://127.0.0.1:8000/api/usuarios/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Ana Pérez\",\"correo\":\"ana@example.com\",\"password\":\"Ana12345\",\"telefono\":\"3019876543\"}"
```

### 2.3 `GET /api/usuarios/{id}/`

Obtiene un usuario por su `id`.

```bash
curl http://127.0.0.1:8000/api/usuarios/1/
```

### 2.4 `PUT /api/usuarios/{id}/`

Actualiza **todos** los campos del usuario.

```bash
curl -X PUT http://127.0.0.1:8000/api/usuarios/1/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Cristian B.\",\"correo\":\"cristian@example.com\",\"password\":\"NuevaClave\",\"telefono\":\"3001234567\",\"activo\":true}"
```

### 2.5 `PATCH /api/usuarios/{id}/`

Actualiza solo los campos enviados.

```bash
curl -X PATCH http://127.0.0.1:8000/api/usuarios/1/ \
  -H "Content-Type: application/json" \
  -d "{\"activo\":false}"
```

### 2.6 `DELETE /api/usuarios/{id}/`

Elimina el usuario. **Cascada**: borra contactos, dispositivos, medicamentos,
horarios, registros y notificaciones asociados.

```bash
curl -X DELETE http://127.0.0.1:8000/api/usuarios/1/
```

**Respuesta:** `204 No Content`.

**Errores comunes:**

- `404 Not Found` — el `id` no existe.
- `400 Bad Request` — correo duplicado o campos faltantes en `POST/PUT`.

---

## 3. Módulo: Contactos

Personas a las que se notificará si el paciente no toma su medicamento.
Cada contacto pertenece a un usuario.

### Esquema del recurso

| Campo        | Tipo    | RW | Descripción                                                       |
|--------------|---------|----|-------------------------------------------------------------------|
| `id`         | integer | R  | Identificador autogenerado.                                       |
| `nombre`     | string  | RW | Nombre del contacto, máx. 100 caracteres.                         |
| `correo`     | string  | RW | Correo del contacto (no único).                                   |
| `telefono`   | string  | RW | Teléfono, máx. 15 caracteres.                                     |
| `id_usuario` | integer | RW | FK hacia `Usuario`. Borrado en cascada.                           |

### 3.1 `GET /api/contactos/`

```bash
curl http://127.0.0.1:8000/api/contactos/
```

**Respuesta 200 OK:**

```json
[
  {
    "id": 1,
    "nombre": "Madre - María",
    "correo": "maria@example.com",
    "telefono": "3024445566",
    "id_usuario": 1
  }
]
```

### 3.2 `POST /api/contactos/`

```bash
curl -X POST http://127.0.0.1:8000/api/contactos/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Madre - María\",\"correo\":\"maria@example.com\",\"telefono\":\"3024445566\",\"id_usuario\":1}"
```

### 3.3 `GET /api/contactos/{id}/`

```bash
curl http://127.0.0.1:8000/api/contactos/1/
```

### 3.4 `PUT /api/contactos/{id}/`

```bash
curl -X PUT http://127.0.0.1:8000/api/contactos/1/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Madre - María L.\",\"correo\":\"maria@example.com\",\"telefono\":\"3024445566\",\"id_usuario\":1}"
```

### 3.5 `PATCH /api/contactos/{id}/`

```bash
curl -X PATCH http://127.0.0.1:8000/api/contactos/1/ \
  -H "Content-Type: application/json" \
  -d "{\"telefono\":\"3027778899\"}"
```

### 3.6 `DELETE /api/contactos/{id}/`

```bash
curl -X DELETE http://127.0.0.1:8000/api/contactos/1/
```

---

## 4. Módulo: Dispositivos

Representa cada ESP32 vinculado a un usuario. Sirve para que el backend
sepa a qué IP enviar (o desde qué IP esperar) las comunicaciones del
pastillero físico.

### Esquema del recurso

| Campo             | Tipo    | RW | Descripción                                                  |
|-------------------|---------|----|--------------------------------------------------------------|
| `id`              | integer | R  | Identificador autogenerado.                                  |
| `nombre`          | string  | RW | Alias del dispositivo (ej. "Pastillero sala"), máx. 100 ch.  |
| `ip_esp32`        | string  | RW | IP del módulo ESP32, máx. 100 caracteres.                    |
| `estado_conexion` | boolean | RW | `true` si el dispositivo está online. Default `false`.       |
| `id_usuario`      | integer | RW | FK hacia `Usuario`. Borrado en cascada.                      |

### 4.1 `GET /api/dispositivos/`

```bash
curl http://127.0.0.1:8000/api/dispositivos/
```

**Respuesta 200 OK:**

```json
[
  {
    "id": 1,
    "nombre": "Pastillero sala",
    "ip_esp32": "192.168.1.50",
    "estado_conexion": true,
    "id_usuario": 1
  }
]
```

### 4.2 `POST /api/dispositivos/`

```bash
curl -X POST http://127.0.0.1:8000/api/dispositivos/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Pastillero sala\",\"ip_esp32\":\"192.168.1.50\",\"estado_conexion\":false,\"id_usuario\":1}"
```

### 4.3 `GET /api/dispositivos/{id}/`

```bash
curl http://127.0.0.1:8000/api/dispositivos/1/
```

### 4.4 `PUT /api/dispositivos/{id}/`

```bash
curl -X PUT http://127.0.0.1:8000/api/dispositivos/1/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Pastillero sala\",\"ip_esp32\":\"192.168.1.51\",\"estado_conexion\":true,\"id_usuario\":1}"
```

### 4.5 `PATCH /api/dispositivos/{id}/`

```bash
curl -X PATCH http://127.0.0.1:8000/api/dispositivos/1/ \
  -H "Content-Type: application/json" \
  -d "{\"estado_conexion\":true}"
```

### 4.6 `DELETE /api/dispositivos/{id}/`

```bash
curl -X DELETE http://127.0.0.1:8000/api/dispositivos/1/
```

---

## 5. Módulo: Medicamentos

Catálogo de medicamentos por usuario.

### Esquema del recurso

| Campo         | Tipo    | RW | Descripción                                                  |
|---------------|---------|----|--------------------------------------------------------------|
| `id`          | integer | R  | Identificador autogenerado.                                  |
| `nombre`      | string  | RW | Nombre comercial o genérico, máx. 100 caracteres.            |
| `descripcion` | string  | RW | Descripción libre (opcional, puede ir vacío).                |
| `dosis`       | string  | RW | Dosis indicada, máx. 50 caracteres (ej. "500 mg", "10 ml"). |
| `id_usuario`  | integer | RW | FK hacia `Usuario`. Borrado en cascada.                      |

### 5.1 `GET /api/medicamentos/`

```bash
curl http://127.0.0.1:8000/api/medicamentos/
```

**Respuesta 200 OK:**

```json
[
  {
    "id": 1,
    "nombre": "Losartán",
    "descripcion": "Antihipertensivo",
    "dosis": "50 mg",
    "id_usuario": 1
  }
]
```

### 5.2 `POST /api/medicamentos/`

```bash
curl -X POST http://127.0.0.1:8000/api/medicamentos/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Losartán\",\"descripcion\":\"Antihipertensivo\",\"dosis\":\"50 mg\",\"id_usuario\":1}"
```

### 5.3 `GET /api/medicamentos/{id}/`

```bash
curl http://127.0.0.1:8000/api/medicamentos/1/
```

### 5.4 `PUT /api/medicamentos/{id}/`

```bash
curl -X PUT http://127.0.0.1:8000/api/medicamentos/1/ \
  -H "Content-Type: application/json" \
  -d "{\"nombre\":\"Losartán\",\"descripcion\":\"Tomar con alimentos\",\"dosis\":\"100 mg\",\"id_usuario\":1}"
```

### 5.5 `PATCH /api/medicamentos/{id}/`

```bash
curl -X PATCH http://127.0.0.1:8000/api/medicamentos/1/ \
  -H "Content-Type: application/json" \
  -d "{\"dosis\":\"100 mg\"}"
```

### 5.6 `DELETE /api/medicamentos/{id}/`

```bash
curl -X DELETE http://127.0.0.1:8000/api/medicamentos/1/
```

---

## 6. Módulo: Horarios

Cada horario indica a qué hora y con qué frecuencia debe tomarse un
medicamento. Incluye un campo calculado `proxima_toma`.

### Esquema del recurso

| Campo                | Tipo                  | RW | Descripción                                                                 |
|----------------------|-----------------------|----|-----------------------------------------------------------------------------|
| `id`                 | integer               | R  | Identificador autogenerado.                                                 |
| `hora_toma`          | string `"HH:MM:SS"`   | RW | Hora base de la primera toma del día.                                       |
| `frecuencia`         | integer (≥ 0)         | RW | Horas entre tomas. `0` significa "una vez al día" en `hora_toma`.           |
| `id_medicamento`     | integer               | RW | FK hacia `Medicamento`. Borrado en cascada.                                 |
| `medicamento_nombre` | string                | R  | Nombre del medicamento asociado (atajo, evita un join desde el cliente).    |
| `proxima_toma`       | string ISO-8601       | R  | Próximo `datetime` calculado, en zona `America/Bogota`. Solo lectura.       |

### Query params soportados

- `id_usuario` (opcional, integer) — devuelve únicamente los horarios cuyos
  medicamentos pertenecen al usuario indicado.

### 6.1 `GET /api/horarios/`

Lista todos los horarios. Si se envía `?id_usuario=`, filtra por dueño.

```bash
curl "http://127.0.0.1:8000/api/horarios/?id_usuario=1"
```

**Respuesta 200 OK:**

```json
[
  {
    "id": 1,
    "hora_toma": "08:00:00",
    "frecuencia": 8,
    "id_medicamento": 1,
    "medicamento_nombre": "Losartán",
    "proxima_toma": "2026-05-26T16:00:00-05:00"
  }
]
```

### 6.2 `POST /api/horarios/`

```bash
curl -X POST http://127.0.0.1:8000/api/horarios/ \
  -H "Content-Type: application/json" \
  -d "{\"hora_toma\":\"08:00:00\",\"frecuencia\":8,\"id_medicamento\":1}"
```

**Validaciones:**

- `frecuencia` debe ser entero ≥ 0 (controlado por el serializer).
- `hora_toma` debe ser una cadena válida `HH:MM` o `HH:MM:SS`.
- `id_medicamento` debe existir; si no, se devuelve 400.

### 6.3 `GET /api/horarios/{id}/`

```bash
curl http://127.0.0.1:8000/api/horarios/1/
```

### 6.4 `PUT /api/horarios/{id}/`

```bash
curl -X PUT http://127.0.0.1:8000/api/horarios/1/ \
  -H "Content-Type: application/json" \
  -d "{\"hora_toma\":\"09:00:00\",\"frecuencia\":12,\"id_medicamento\":1}"
```

### 6.5 `PATCH /api/horarios/{id}/`

```bash
curl -X PATCH http://127.0.0.1:8000/api/horarios/1/ \
  -H "Content-Type: application/json" \
  -d "{\"frecuencia\":6}"
```

### 6.6 `DELETE /api/horarios/{id}/`

```bash
curl -X DELETE http://127.0.0.1:8000/api/horarios/1/
```

---

## 7. Módulo: Registros de toma

Cada registro almacena la programación esperada y la hora real en la que
el medicamento fue tomado. Es la base para calcular adherencia.

### Esquema del recurso

| Campo                   | Tipo            | RW | Descripción                                                              |
|-------------------------|-----------------|----|--------------------------------------------------------------------------|
| `id`                    | integer         | R  | Identificador autogenerado.                                              |
| `fecha_hora_programada` | datetime ISO-8601 | RW | Momento esperado de la toma.                                            |
| `fecha_hora_real`       | datetime ISO-8601 | RW | Momento en que ocurrió la toma. Puede ser `null` si aún no se confirmó. |
| `id_horario`            | integer         | RW | FK hacia `Horario`. Borrado en cascada.                                  |
| `id_usuario`            | integer         | RW | FK hacia `Usuario`. Borrado en cascada.                                  |

### 7.1 `GET /api/registros/`

```bash
curl http://127.0.0.1:8000/api/registros/
```

**Respuesta 200 OK:**

```json
[
  {
    "id": 1,
    "fecha_hora_programada": "2026-05-26T08:00:00-05:00",
    "fecha_hora_real": "2026-05-26T08:05:12-05:00",
    "id_horario": 1,
    "id_usuario": 1
  }
]
```

### 7.2 `POST /api/registros/`

```bash
curl -X POST http://127.0.0.1:8000/api/registros/ \
  -H "Content-Type: application/json" \
  -d "{\"fecha_hora_programada\":\"2026-05-26T08:00:00-05:00\",\"fecha_hora_real\":null,\"id_horario\":1,\"id_usuario\":1}"
```

### 7.3 `GET /api/registros/{id}/`

```bash
curl http://127.0.0.1:8000/api/registros/1/
```

### 7.4 `PUT /api/registros/{id}/`

```bash
curl -X PUT http://127.0.0.1:8000/api/registros/1/ \
  -H "Content-Type: application/json" \
  -d "{\"fecha_hora_programada\":\"2026-05-26T08:00:00-05:00\",\"fecha_hora_real\":\"2026-05-26T08:05:12-05:00\",\"id_horario\":1,\"id_usuario\":1}"
```

### 7.5 `PATCH /api/registros/{id}/`

Use este endpoint para "confirmar" la toma cuando el ESP32 reporta el evento:

```bash
curl -X PATCH http://127.0.0.1:8000/api/registros/1/ \
  -H "Content-Type: application/json" \
  -d "{\"fecha_hora_real\":\"2026-05-26T08:05:12-05:00\"}"
```

### 7.6 `DELETE /api/registros/{id}/`

```bash
curl -X DELETE http://127.0.0.1:8000/api/registros/1/
```

---

## 8. Módulo: Notificaciones

Mensajes enviados a los contactos cuando una toma falla, se omite o se
requiere alertar.

### Esquema del recurso

| Campo          | Tipo              | RW | Descripción                                                |
|----------------|-------------------|----|------------------------------------------------------------|
| `id`           | integer           | R  | Identificador autogenerado.                                |
| `mensaje`      | string            | RW | Texto de la notificación, máx. 255 caracteres.             |
| `fecha_envio`  | datetime ISO-8601 | R  | Generado automáticamente al crear (`auto_now_add`).        |
| `id_registro`  | integer           | RW | FK hacia `Registro_Toma`. Borrado en cascada.              |
| `id_contacto`  | integer           | RW | FK hacia `Contacto`. Borrado en cascada.                   |

### 8.1 `GET /api/notificaciones/`

```bash
curl http://127.0.0.1:8000/api/notificaciones/
```

**Respuesta 200 OK:**

```json
[
  {
    "id": 1,
    "mensaje": "Cristian no tomó su Losartán de las 8:00",
    "fecha_envio": "2026-05-26T08:30:00-05:00",
    "id_registro": 1,
    "id_contacto": 1
  }
]
```

### 8.2 `POST /api/notificaciones/`

```bash
curl -X POST http://127.0.0.1:8000/api/notificaciones/ \
  -H "Content-Type: application/json" \
  -d "{\"mensaje\":\"Cristian no tomó su Losartán de las 8:00\",\"id_registro\":1,\"id_contacto\":1}"
```

### 8.3 `GET /api/notificaciones/{id}/`

```bash
curl http://127.0.0.1:8000/api/notificaciones/1/
```

### 8.4 `PUT /api/notificaciones/{id}/`

```bash
curl -X PUT http://127.0.0.1:8000/api/notificaciones/1/ \
  -H "Content-Type: application/json" \
  -d "{\"mensaje\":\"Toma omitida confirmada\",\"id_registro\":1,\"id_contacto\":1}"
```

### 8.5 `PATCH /api/notificaciones/{id}/`

```bash
curl -X PATCH http://127.0.0.1:8000/api/notificaciones/1/ \
  -H "Content-Type: application/json" \
  -d "{\"mensaje\":\"Mensaje actualizado\"}"
```

### 8.6 `DELETE /api/notificaciones/{id}/`

```bash
curl -X DELETE http://127.0.0.1:8000/api/notificaciones/1/
```

---

## 9. Módulo: Próximos horarios

Endpoint pensado para alimentar el dashboard de la SPA. Devuelve los cinco
próximos horarios ordenados por `hora_toma`, ya con el cálculo de
`proxima_toma` realizado por el servidor.

### 9.1 `GET /api/proximos-horarios/?id_usuario={id}`

**Query params:**

| Param        | Tipo    | Requerido | Descripción                       |
|--------------|---------|-----------|-----------------------------------|
| `id_usuario` | integer | Sí        | Usuario cuyos horarios se buscan. |

**Respuesta 200 OK:**

```json
[
  {
    "medicamento": "Losartán",
    "hora_toma": "08:00",
    "frecuencia": 8,
    "proxima_toma": "2026-05-26T16:00:00-05:00"
  },
  {
    "medicamento": "Acetaminofén",
    "hora_toma": "14:00",
    "frecuencia": 6,
    "proxima_toma": "2026-05-26T14:00:00-05:00"
  }
]
```

**Respuesta 400 Bad Request** (falta el parámetro):

```json
{ "error": "Falta id_usuario" }
```

**Ejemplo `curl`:**

```bash
curl "http://127.0.0.1:8000/api/proximos-horarios/?id_usuario=1"
```

---

## 10. Códigos de error comunes

| Código | Significado                  | Cuándo ocurre                                                            |
|--------|------------------------------|--------------------------------------------------------------------------|
| 200    | OK                           | Lectura o actualización exitosa.                                         |
| 201    | Created                      | Creación exitosa (`POST`).                                               |
| 204    | No Content                   | Eliminación exitosa (`DELETE`).                                          |
| 400    | Bad Request                  | Campos faltantes, validaciones fallidas, FK inexistente.                 |
| 401    | Unauthorized                 | `login` con credenciales inválidas.                                      |
| 404    | Not Found                    | El recurso `{id}` no existe.                                             |
| 405    | Method Not Allowed           | Método HTTP no permitido para esa URL.                                   |
| 500    | Internal Server Error        | Error inesperado (revisa la consola de Django para el traceback).        |

### Ejemplos de cuerpos de error

**Validación fallida:**

```json
{
  "correo": ["Introduzca una dirección de correo electrónico válida."],
  "telefono": ["Este campo es requerido."]
}
```

**Recurso no encontrado:**

```json
{ "detail": "No encontrado." }
```

**Método no permitido:**

```json
{ "detail": "Método \"GET\" no permitido." }
```
