# API Pillbox — Diccionario de Datos

Documento que describe la base de datos relacional utilizada por el backend
`api_pillbox`. Incluye descripción de tablas, columnas, tipos, restricciones,
relaciones, índices y reglas de negocio implícitas.

---

## 1. Información general

| Atributo                    | Valor                                                       |
|-----------------------------|-------------------------------------------------------------|
| Motor                       | PostgreSQL 13 o superior                                    |
| Nombre de la base de datos  | `pillbox_db`                                                |
| Host por defecto            | `localhost`                                                 |
| Puerto                      | `5432`                                                      |
| Usuario por defecto         | `postgres`                                                  |
| Contraseña por defecto      | `0000` (cambiar antes de cualquier despliegue)              |
| Charset                     | UTF-8                                                       |
| Zona horaria de la app      | `America/Bogota` (`USE_TZ = True`)                          |
| ORM                         | Django ORM (modelos en `core/models.py`)                    |
| Prefijo de tablas           | `core_` (Django agrega el nombre de la app)                 |

> Las tablas se crean automáticamente con `python manage.py migrate`. La
> definición canónica está en los modelos Django; lo que aquí se describe
> es el esquema resultante en PostgreSQL.

---

## 2. Modelo Entidad–Relación (resumen)

```
Usuario (1) ──< Contacto (N)
Usuario (1) ──< Dispositivo (N)
Usuario (1) ──< Medicamento (N)
Usuario (1) ──< Registro_Toma (N)

Medicamento (1) ──< Horario (N)
Horario (1) ──< Registro_Toma (N)

Registro_Toma (1) ──< Notificacion (N)
Contacto      (1) ──< Notificacion (N)
```

Todas las relaciones FK están definidas con `ON DELETE CASCADE`, lo que
significa que al borrar un padre se eliminan automáticamente los hijos.

---

## 3. Tablas

### 3.1 `core_usuario`

Almacena los usuarios principales del sistema (pacientes / responsables del
pastillero).

| Columna           | Tipo PostgreSQL          | Nulo | Default        | Restricciones / Comentario                                       |
|-------------------|--------------------------|------|----------------|------------------------------------------------------------------|
| `id`              | `bigint`                 | No   | secuencia      | **PK**. Autoincremental (`BigAutoField`).                        |
| `nombre`          | `varchar(100)`           | No   | —              | Nombre del usuario.                                              |
| `correo`          | `varchar(254)`           | No   | —              | **UNIQUE**. Validado como email.                                 |
| `password`        | `varchar(100)`           | No   | —              | Contraseña en **texto plano** (limitación del diseño actual).    |
| `telefono`        | `varchar(15)`            | No   | —              | Teléfono de contacto.                                            |
| `activo`          | `boolean`                | No   | `true`         | Marca lógica de habilitación.                                    |
| `fecha_creacion`  | `timestamp with time zone` | No | `now()`        | Fecha y hora del alta.                                           |

**Índices:**
- `PRIMARY KEY (id)`
- `UNIQUE (correo)`

**Relaciones salientes:** ninguna.
**Relaciones entrantes:** `Contacto`, `Dispositivo`, `Medicamento`,
`Registro_Toma` (todas vía `id_usuario`, `ON DELETE CASCADE`).

---

### 3.2 `core_contacto`

Contactos de emergencia que serán notificados cuando una toma falla o se
omite.

| Columna         | Tipo PostgreSQL  | Nulo | Default | Restricciones / Comentario                                  |
|-----------------|------------------|------|---------|-------------------------------------------------------------|
| `id`            | `bigint`         | No   | secuencia | **PK**. Autoincremental.                                  |
| `nombre`        | `varchar(100)`   | No   | —       | Nombre o alias del contacto.                                |
| `correo`        | `varchar(254)`   | No   | —       | Correo del contacto (no único).                             |
| `telefono`      | `varchar(15)`    | No   | —       | Teléfono del contacto.                                      |
| `id_usuario_id` | `bigint`         | No   | —       | **FK** → `core_usuario.id`. `ON DELETE CASCADE`.            |

**Índices:**
- `PRIMARY KEY (id)`
- `INDEX (id_usuario_id)` (creado por Django para la FK)

> **Nota Django:** en el modelo el campo se llama `id_usuario`, pero
> PostgreSQL lo almacena como `id_usuario_id` (Django agrega `_id` a las
> columnas que son `ForeignKey`).

---

### 3.3 `core_dispositivo`

Cada ESP32 vinculado a un usuario.

| Columna             | Tipo PostgreSQL | Nulo | Default | Restricciones / Comentario                                      |
|---------------------|-----------------|------|---------|-----------------------------------------------------------------|
| `id`                | `bigint`        | No   | secuencia | **PK**. Autoincremental.                                      |
| `nombre`            | `varchar(100)`  | No   | —       | Alias del dispositivo (ej. "Pastillero sala").                  |
| `ip_esp32`          | `varchar(100)`  | No   | —       | IP del ESP32. No tiene formato validado: cadena libre.          |
| `estado_conexion`   | `boolean`       | No   | `false` | `true` si se reporta online.                                    |
| `id_usuario_id`     | `bigint`        | No   | —       | **FK** → `core_usuario.id`. `ON DELETE CASCADE`.                |

**Índices:**
- `PRIMARY KEY (id)`
- `INDEX (id_usuario_id)`

---

### 3.4 `core_medicamento`

Catálogo de medicamentos por usuario.

| Columna         | Tipo PostgreSQL | Nulo | Default | Restricciones / Comentario                                  |
|-----------------|-----------------|------|---------|-------------------------------------------------------------|
| `id`            | `bigint`        | No   | secuencia | **PK**.                                                   |
| `nombre`        | `varchar(100)`  | No   | —       | Nombre del medicamento.                                     |
| `descripcion`   | `text`          | No   | `''`    | Notas o instrucciones (puede ir vacío, `blank=True`).       |
| `dosis`         | `varchar(50)`   | No   | —       | Dosis indicada (ej. "50 mg").                               |
| `id_usuario_id` | `bigint`        | No   | —       | **FK** → `core_usuario.id`. `ON DELETE CASCADE`.            |

**Índices:**
- `PRIMARY KEY (id)`
- `INDEX (id_usuario_id)`

---

### 3.5 `core_horario`

Frecuencia y hora base para tomar cada medicamento.

| Columna             | Tipo PostgreSQL | Nulo | Default | Restricciones / Comentario                                                       |
|---------------------|-----------------|------|---------|----------------------------------------------------------------------------------|
| `id`                | `bigint`        | No   | secuencia | **PK**.                                                                        |
| `hora_toma`         | `time`          | No   | —       | Hora base de la primera toma del día (sin fecha).                                |
| `frecuencia`        | `integer`       | No   | `0`     | Horas entre tomas (≥ 0). Migrado desde `varchar` a `PositiveIntegerField` en la migración 0006. `0` ⇒ "una sola toma diaria". |
| `id_medicamento_id` | `bigint`        | No   | —       | **FK** → `core_medicamento.id`. `ON DELETE CASCADE`.                            |

**Índices:**
- `PRIMARY KEY (id)`
- `INDEX (id_medicamento_id)`

**Campo calculado (no persistido):**
- `proxima_toma` — `datetime` aware (`America/Bogota`). Se calcula en el
  modelo a partir de `hora_toma`, `frecuencia` y el reloj del servidor.

---

### 3.6 `core_registro_toma`

Historial de cada toma programada y, opcionalmente, ejecutada.

| Columna                  | Tipo PostgreSQL              | Nulo | Default | Restricciones / Comentario                                  |
|--------------------------|------------------------------|------|---------|-------------------------------------------------------------|
| `id`                     | `bigint`                     | No   | secuencia | **PK**.                                                   |
| `fecha_hora_programada`  | `timestamp with time zone`   | No   | —       | Momento esperado de la toma.                                |
| `fecha_hora_real`        | `timestamp with time zone`   | **Sí** | `NULL`  | Momento real de la toma. `NULL` ⇒ aún no ocurrió o se omitió. |
| `id_horario_id`          | `bigint`                     | No   | —       | **FK** → `core_horario.id`. `ON DELETE CASCADE`.            |
| `id_usuario_id`          | `bigint`                     | No   | —       | **FK** → `core_usuario.id`. `ON DELETE CASCADE`.            |

**Índices:**
- `PRIMARY KEY (id)`
- `INDEX (id_horario_id)`
- `INDEX (id_usuario_id)`

**Regla de negocio:**
- Si `fecha_hora_real` es `NULL` y ya pasó `fecha_hora_programada`, la toma
  se considera **omitida** y debería disparar la creación de una
  `Notificacion` hacia los contactos del usuario.

---

### 3.7 `core_notificacion`

Mensajes enviados a contactos de emergencia.

| Columna         | Tipo PostgreSQL              | Nulo | Default        | Restricciones / Comentario                                  |
|-----------------|------------------------------|------|----------------|-------------------------------------------------------------|
| `id`            | `bigint`                     | No   | secuencia      | **PK**.                                                     |
| `mensaje`       | `varchar(255)`               | No   | —              | Texto de la notificación.                                   |
| `fecha_envio`   | `timestamp with time zone`   | No   | `now()` (`auto_now_add`) | Se llena automáticamente al crear el registro.      |
| `id_registro_id`| `bigint`                     | No   | —              | **FK** → `core_registro_toma.id`. `ON DELETE CASCADE`.      |
| `id_contacto_id`| `bigint`                     | No   | —              | **FK** → `core_contacto.id`. `ON DELETE CASCADE`.           |

**Índices:**
- `PRIMARY KEY (id)`
- `INDEX (id_registro_id)`
- `INDEX (id_contacto_id)`

---

## 4. Tablas internas de Django (informativo)

Las migraciones de Django crean además las siguientes tablas internas
necesarias para autenticación, admin y sesiones:

- `django_migrations`
- `django_content_type`
- `auth_user`, `auth_group`, `auth_permission` y sus tablas pivote
- `django_admin_log`
- `django_session`

> Estas tablas **no** son utilizadas directamente por el modelo de negocio
> de `core`. La autenticación de la API se hace contra `core_usuario`, no
> contra `auth_user`. `auth_user` solo se usa si creas superusuarios para
> el panel `/admin/`.

---

## 5. Relaciones y reglas de integridad

| Relación                                    | Tipo | Cardinalidad | Borrado en cascada |
|---------------------------------------------|------|--------------|--------------------|
| `core_contacto.id_usuario_id`       → `core_usuario.id`       | FK | N : 1 | Sí |
| `core_dispositivo.id_usuario_id`    → `core_usuario.id`       | FK | N : 1 | Sí |
| `core_medicamento.id_usuario_id`    → `core_usuario.id`       | FK | N : 1 | Sí |
| `core_horario.id_medicamento_id`    → `core_medicamento.id`   | FK | N : 1 | Sí |
| `core_registro_toma.id_horario_id`  → `core_horario.id`       | FK | N : 1 | Sí |
| `core_registro_toma.id_usuario_id`  → `core_usuario.id`       | FK | N : 1 | Sí |
| `core_notificacion.id_registro_id`  → `core_registro_toma.id` | FK | N : 1 | Sí |
| `core_notificacion.id_contacto_id`  → `core_contacto.id`      | FK | N : 1 | Sí |

> Eliminar un `Usuario` borra absolutamente todos sus contactos,
> dispositivos, medicamentos, horarios (vía medicamento), registros y
> notificaciones (vía registro y contacto).

---

## 6. Historial de migraciones relevantes

Las migraciones viven en `core/migrations/`. Los cambios importantes:

| Archivo                                        | Cambio principal                                                                                  |
|------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `0001_initial.py`                              | Creación inicial de todas las tablas con `frecuencia` como `varchar(50)` y `contraseña` con eñe. |
| `0002_rename_contraseña_usuario_password.py`   | Renombra `contraseña` → `password` para evitar problemas con caracteres no ASCII.                |
| `0003_usuario_activo.py`                       | Agrega la bandera `activo` a `usuario`.                                                          |
| `0004_alter_usuario_activo.py`                 | Ajusta el default de `activo`.                                                                   |
| `0005_usuario_fecha_creacion.py`               | Agrega la columna `fecha_creacion`.                                                              |
| `0006_alter_horario_frecuencia.py`             | Convierte `frecuencia` de texto a entero positivo. Migra datos antiguos extrayendo el primer número que aparezca en la cadena. |

---

## 7. Diagrama lógico (texto)

```
┌─────────────────────────┐
│       core_usuario      │
├─────────────────────────┤
│ id            (PK)      │
│ nombre        varchar   │
│ correo        UNIQUE    │
│ password      varchar   │
│ telefono      varchar   │
│ activo        bool      │
│ fecha_creacion timestamptz │
└──────┬──────┬──────┬────┘
       │      │      │
       │      │      └────────────────────────────┐
       │      └────────────────────────┐          │
       │                               │          │
       ▼                               ▼          ▼
┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ core_contacto│  │ core_dispositivo │  │ core_medicamento│
├──────────────┤  ├──────────────────┤  ├─────────────────┤
│ id (PK)      │  │ id (PK)          │  │ id (PK)         │
│ nombre       │  │ nombre           │  │ nombre          │
│ correo       │  │ ip_esp32         │  │ descripcion     │
│ telefono     │  │ estado_conexion  │  │ dosis           │
│ id_usuario_id│  │ id_usuario_id    │  │ id_usuario_id   │
└──────┬───────┘  └──────────────────┘  └────────┬────────┘
       │                                          │
       │                                          ▼
       │                                ┌──────────────────┐
       │                                │   core_horario   │
       │                                ├──────────────────┤
       │                                │ id (PK)          │
       │                                │ hora_toma        │
       │                                │ frecuencia       │
       │                                │ id_medicamento_id│
       │                                └────────┬─────────┘
       │                                         │
       │                                         ▼
       │                            ┌─────────────────────────┐
       │                            │    core_registro_toma   │
       │                            ├─────────────────────────┤
       │                            │ id (PK)                 │
       │                            │ fecha_hora_programada   │
       │                            │ fecha_hora_real (NULL)  │
       │                            │ id_horario_id           │
       │                            │ id_usuario_id           │
       │                            └────────────┬────────────┘
       │                                         │
       │              ┌──────────────────────────┘
       │              ▼
       │   ┌──────────────────────┐
       └──►│   core_notificacion  │
           ├──────────────────────┤
           │ id (PK)              │
           │ mensaje              │
           │ fecha_envio          │
           │ id_registro_id       │
           │ id_contacto_id       │
           └──────────────────────┘
```

---

## 8. Consideraciones y deuda técnica

- **Contraseñas en texto plano**: la tabla `core_usuario` guarda
  `password` sin hash. Antes de producción debería migrarse a
  `make_password` (PBKDF2) y validarse con `check_password`.
- **Sin índice único por `(id_usuario_id, ip_esp32)`**: nada impide que
  dos dispositivos del mismo usuario tengan la misma IP.
- **`ALLOWED_HOSTS` vacío**: la API solo funciona con `DEBUG=True`. Para
  producción se debe definir.
- **`frecuencia = 0`**: aceptado por el modelo (default histórico de la
  migración 0006). Significa "una vez al día"; cualquier código que
  recorra horarios futuros debe contemplar ese caso.
- **Sin tabla de tokens**: la autenticación es estado-cero (no hay JWT
  ni `auth_token`); el cliente recibe los datos del usuario en el login
  y debe manejar la sesión en el front.
