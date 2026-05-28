# GestionAgua API

API REST para la gestión de agua potable rural. Permite administrar socios, medidores, lecturas de consumo, boletas, cortes de servicio y reportes.

## Stack tecnológico

- **Python** 3.x
- **Django** 4.2
- **Django REST Framework** 3.16
- **SimpleJWT** 5.5 — autenticación con tokens JWT
- **PostgreSQL** — base de datos principal
- **pytest-django** — suite de tests
- **python-decouple** — gestión de variables de entorno

## Módulos

| Módulo | Descripción |
|---|---|
| `usuarios` | Usuario personalizado con roles (administrador, operador, funcionario, socio) |
| `socios` | Socios, rutas y medidores |
| `lecturas` | Registro de lecturas de consumo por período |
| `boletas` | Generación de boletas (en desarrollo) |
| `cortes` | Cortes de servicio (en desarrollo) |
| `reportes` | Reportes (en desarrollo) |

---

## Requisitos previos

- Python 3.10+
- PostgreSQL 14+
- `pip`

---

## Entornos

El proyecto tiene settings separados por entorno ubicados en `gestionaguaApp/settings/`:

| Archivo | Entorno | `DEBUG` | Descripción |
|---|---|---|---|
| `base.py` | — | — | Configuración compartida |
| `development.py` | Desarrollo | `True` | Configuración local |
| `production.py` | Producción | `False` | Seguridad activa, archivos estáticos recolectados |

El entorno se selecciona con la variable `DJANGO_SETTINGS_MODULE`. Por defecto `manage.py` y `wsgi.py` apuntan a `development`.

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd gestionaguaProject
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install django djangorestframework djangorestframework-simplejwt \
    psycopg2-binary python-decouple pytest pytest-django pytest-cov
```

---

## Desarrollo local

### 1. Configurar `.env`

Crea el archivo `.env` dentro de `gestionaguaApp/` (junto a `manage.py`):

```env
SECRET_KEY=django-insecure-clave-solo-para-desarrollo
DB_NAME=gestion_agua
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Crear la base de datos

```bash
psql -U postgres -c "CREATE DATABASE gestion_agua;"
```

### 3. Aplicar migraciones

```bash
cd gestionaguaApp
python manage.py migrate
```

### 4. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 5. Levantar el servidor

```bash
python manage.py runserver
```

El servidor queda disponible en `http://127.0.0.1:8000/`.

> `manage.py` usa `gestionaguaApp.settings.development` por defecto. No necesitas exportar ninguna variable.

---

## Producción

### 1. Configurar `.env` de producción

El archivo `.env` debe estar en el servidor, dentro de `gestionaguaApp/`. Usa variables distintas a las de desarrollo:

```env
SECRET_KEY_PROD=clave-secreta-larga-y-aleatoria-para-produccion
DB_NAME=gestion_agua_prod
DB_USER=usuario_prod
DB_PASSWORD=password_seguro
DB_HOST=host-de-base-de-datos
DB_PORT=5432
ALLOWED_HOSTS=tudominio.cl,www.tudominio.cl
```

> `SECRET_KEY_PROD` es independiente de `SECRET_KEY`. Nunca reutilices la clave de desarrollo en producción.

### 2. Apuntar al settings de producción

Exporta la variable antes de cualquier comando de Django:

```bash
export DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production
```

O pásala directamente en cada comando:

```bash
DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production python manage.py migrate
```

### 3. Aplicar migraciones

```bash
cd gestionaguaApp
DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production python manage.py migrate
```

### 4. Recolectar archivos estáticos

```bash
DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production python manage.py collectstatic --no-input
```

Los archivos quedan en `gestionaguaApp/staticfiles/`.

### 5. Levantar con Gunicorn

Instala Gunicorn si no lo tienes:

```bash
pip install gunicorn
```

Levanta el servidor WSGI:

```bash
cd gestionaguaApp
DJANGO_SETTINGS_MODULE=gestionaguaApp.settings.production \
    gunicorn gestionaguaApp.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

> En producción se recomienda poner Nginx como proxy inverso delante de Gunicorn.

### 6. Nginx (ejemplo mínimo)

```nginx
server {
    listen 80;
    server_name tudominio.cl;

    location /static/ {
        alias /ruta/al/proyecto/gestionaguaApp/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Ejecutar el servidor (desarrollo rápido)

---

## Autenticación JWT

Todos los endpoints requieren autenticación con token JWT.

### Obtener token

```bash
POST /api/token/
Content-Type: application/json

{
  "username": "tu_usuario",
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "access": "<token_de_acceso>",
  "refresh": "<token_de_refresco>",
  "rol": "administrador"
}
```

### Refrescar token

```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "<token_de_refresco>"
}
```

### Cerrar sesión (invalidar token)

```bash
POST /api/token/blacklist/
Authorization: Bearer <token_de_acceso>
Content-Type: application/json

{
  "refresh": "<token_de_refresco>"
}
```

### Uso en peticiones

Incluir el header en cada petición autenticada:

```
Authorization: Bearer <token_de_acceso>
```

---

## Endpoints disponibles

### Socios — `/socios/`

| Método | URL | Descripción |
|---|---|---|
| GET | `/socios/` | Listar todos los socios |
| GET | `/socios/buscar/?nombre=...` | Buscar socio por nombre/apellido |
| POST | `/socios/agregar/` | Crear nuevo socio |
| PUT | `/socios/actualizar/<id>/` | Actualizar socio |
| DELETE | `/socios/eliminar/<id>/` | Eliminar socio |

### Lecturas — `/lecturas/`

| Método | URL | Descripción |
|---|---|---|
| GET | `/lecturas/` | Listar todas las lecturas |
| POST | `/lecturas/agregar/` | Registrar nueva lectura |
| GET | `/lecturas/buscar/<id>/` | Obtener lectura por ID |
| PUT | `/lecturas/actualizar/<id>/` | Actualizar lectura |

### Administración

| URL | Descripción |
|---|---|
| `/admin/` | Panel de administración de Django |

---

## Estructura del proyecto

```
gestionaguaProject/
├── .env                        # Variables de entorno (no versionar)
├── README.md
└── gestionaguaApp/
    ├── manage.py
    ├── pytest.ini
    ├── settings/               # Settings por entorno
    |   |── __init__.py
    │   ├── base.py
    │   ├── development.py
    │   └── production.py
    ├── gestionaguaApp/         # Configuración del proyecto
    │   └── urls.py
    ├── usuarios/               # Modelo de usuario personalizado
    ├── socios/                 # Socios, medidores y rutas
    ├── lecturas/               # Lecturas de consumo
    ├── boletas/                # (en desarrollo)
    ├── cortes/                 # (en desarrollo)
    └── reportes/               # (en desarrollo)
```

---

## Tests

```bash
cd gestionaguaApp
pytest
```

Con reporte de cobertura:

```bash
pytest --cov=. --cov-report=term-missing
```

---

## Variables de entorno

### Desarrollo (`settings/development.py`)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | `django-insecure-...` |
| `DB_NAME` | Nombre de la base de datos | `gestion_agua` |
| `DB_USER` | Usuario de PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `tu_password` |
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |

### Producción (`settings/production.py`)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SECRET_KEY_PROD` | Clave secreta de producción (distinta a dev) | `clave-aleatoria-larga` |
| `DB_NAME` | Nombre de la base de datos | `gestion_agua_prod` |
| `DB_USER` | Usuario de PostgreSQL | `usuario_prod` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `password_seguro` |
| `DB_HOST` | Host de PostgreSQL | `db.servidor.cl` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `tudominio.cl,www.tudominio.cl` |
