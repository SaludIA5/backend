# SALUAI 5 Backend

Backend del proyecto **SALUAI 5** desarrollado en Python con FastAPI y PostgreSQL.

## Stack Tecnológico

- **Lenguaje:** Python 3.10
- **Framework Web:** FastAPI
- **ORM:** SQLAlchemy (async)
- **Migraciones:** Alembic
- **Base de Datos:** PostgreSQL
- **Autenticación:** python-jose, passlib, bcrypt
- **Configuración:** pydantic, dotenv
- **Servidor ASGI:** Uvicorn
- **Contenedores:** Docker, Docker Compose

## Principales dependencias

- [`fastapi`](https://fastapi.tiangolo.com/) - Framework web moderno y rápido.
- [`sqlalchemy`](https://www.sqlalchemy.org/) - ORM para manejo de base de datos.
- [`alembic`](https://alembic.sqlalchemy.org/) - Migraciones de base de datos.
- [`asyncpg`](https://github.com/MagicStack/asyncpg) - Driver asíncrono para PostgreSQL.
- [`aiomysql`](https://aiomysql.readthedocs.io/) - Driver asíncrono para MySQL (opcional).
- [`python-jose`](https://python-jose.readthedocs.io/) - Manejo de JWT y autenticación.
- [`passlib`](https://passlib.readthedocs.io/) y [`bcrypt`](https://pypi.org/project/bcrypt/) - Hashing de contraseñas.
- [`pydantic`](https://docs.pydantic.dev/) y [`pydantic-settings`](https://docs.pydantic.dev/latest/usage/pydantic_settings/) - Validación y gestión de configuración.
- [`python-dotenv`](https://saurabh-kumar.com/python-dotenv/) - Carga de variables de entorno desde `.env`.
- [`uvicorn`](https://www.uvicorn.org/) - Servidor ASGI para FastAPI.

## Estructura del proyecto

```
.
├── app/
│   ├── api/
│   ├── alembic/
│   ├── core/
│   ├── databases/
│   ├── main.py
│   └── params.py
├── run.py
├── start.sh
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
└── .env
```
## Configuración de variables de entorno

Asegúrate de configurar correctamente las variables en el archivo `.env` según el entorno en el que vayas a ejecutar el proyecto:

- **Con Docker:**  
  Usa el valor por defecto para conectar con el contenedor de la base de datos:
  ```env
  BACKEND_DB_PSQL_HOST="postgresql_db"
  ```

- **Ejecución local:**  
  Si ejecutas el backend y la base de datos en tu máquina local, usa:
  ```env
  BACKEND_DB_PSQL_HOST="localhost"
  ```

**El archivo .env se debe colocar en la raiz del proyecto. El resto de las variables de entorno se encuentran en el grupo de wsp de backend.**

## Uso

### Levantar el entorno de desarrollo

```sh
docker-compose up --build
```

Esto ejecutará las migraciones y levantará el backend en `http://localhost:8000`.

### Ejecutar localmente

1. Instala las dependencias:
    ```sh
    poetry install
    ```
2. Crea un archivo `.env` en la raíz con las variables necesarias.
3. Ejecuta las migraciones:
    ```sh
    poetry run alembic -c app/alembic.ini upgrade head
    ```
4. Inicia el servidor:
    ```sh
    poetry run python run.py
    ```
### Linter y formateo de código

Usamos **Black**, **Isort** y **Flake8** para mantener un estilo de código consistente.

- Revisar estilo:

```sh
poetry run black --check .
poetry run isort --check-only .
poetry run flake8 .
```

Arreglar formato automáticamente:

```sh
poetry run black .
poetry run isort .
```

### Pre-commit hooks

Para evitar subir código mal formateado, usamos `pre-commit`.

- Instalar hooks:

```sh
poetry run pre-commit install
```

Cada vez que hagas commit, correrán Black, Isort y Flake8 automáticamente.

- Para correr los checks manualmente en todo el repo:

```sh
poetry run pre-commit run --all-files
```

### CI con GitHub Actions

El pipeline se ejecuta en cada push y pull request a `main`.
Este flujo hace lo siguiente:

- Instala dependencias con Poetry.
- Corre linters (Black, Isort, Flake8).
- Corre los tests (pytest).

Archivo del workflow: `.github/workflows/ci.yml`


## Endpoints principales

- `/` - Endpoint raíz, mensaje de bienvenida.
- `/health` - Endpoint de health check.

---

> Para más detalles, revisa la configuración en [`app/core/config.py`](app/core/config.py) y los routers en [`app/api/router.py`](app/api/router.py).