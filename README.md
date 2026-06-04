# SISPRO — Sistema de Inventario y Optimización

**URL:** [https://proyecto-dev-2026-1-1.onrender.com](https://proyecto-dev-2026-1-1.onrender.com)

Sistema web de gestión de inventarios con optimización basada en el modelo EOQ (Economic Order Quantity). Permite administrar productos, proveedores y ventas, y genera recomendaciones inteligentes de pedido para mantener niveles óptimos de stock.

---

## Características

- **CRUD completo** de productos, proveedores y ventas con formularios HTML y API REST
- **Dashboard** con KPIs (totales), gráfica de ventas mensuales (CSS puro) y distribución de stock
- **Motor de optimización EOQ** que calcula cantidad económica de pedido, punto de reorden, stock de seguridad y alertas (Óptimo, Próximo pedido, Pedir ahora, Urgente)
- **Búsqueda** integrada con paginación en todas las vistas
- **Subida de imágenes** a Supabase Storage (productos y logos de proveedores)
- **Validación** de datos tanto en frontend como en backend
- **Descuento automático de stock** al registrar una venta
- **Eliminación lógica** (soft delete) para productos y proveedores
- **Interfaz responsive** con diseño dark neon glassmorphism
- **API REST documentada** con rutas para integración externa

---

## Tecnologías

| Categoría      | Tecnología                                           |
| -------------- | ---------------------------------------------------- |
| Lenguaje       | Python 3.11+                                         |
| Framework      | FastAPI                                              |
| Servidor ASGI  | Uvicorn                                              |
| ORM            | SQLModel (SQLAlchemy + Pydantic)                     |
| Base de datos  | PostgreSQL (Neon.tech)                               |
| Almacenamiento | Supabase Storage                                     |
| Templates      | Jinja2                                               |
| Frontend       | CSS personalizado + Vanilla JS                       |
| Testing        | pytest + pytest-asyncio + httpx                      |
| Contenedor     | Docker                                               |
| Gestor de dependencias | uv                                                   |

---

## Estructura del proyecto

```
proyecto-dev-2026/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuración con variables de entorno
│   │   ├── database.py        # Conexión a PostgreSQL (async)
│   │   ├── storage.py         # Cliente Supabase Storage
│   │   └── templates.py       # Configuración de Jinja2
│   ├── logic/
│   │   └── math.py            # Motor de optimización EOQ
│   ├── models/
│   │   ├── producto.py        # Modelo y schemas de producto
│   │   ├── proveedor.py       # Modelo y schemas de proveedor
│   │   ├── venta.py           # Modelo y schemas de venta
│   │   └── orden_sugerida.py  # Modelo de respuesta de optimización
│   ├── repository/
│   │   ├── producto_repo.py   # Acceso a datos de productos
│   │   ├── proveedor_repo.py  # Acceso a datos de proveedores
│   │   └── venta_repo.py      # Acceso a datos de ventas
│   ├── routes/
│   │   ├── pages.py                # Rutas SSR (HTML)
│   │   ├── productos_routes.py     # API REST productos
│   │   ├── proveedores_routes.py   # API REST proveedores
│   │   ├── ventas_routes.py        # API REST ventas
│   │   ├── optimizacion_routes.py  # API REST optimización EOQ
│   │   └── dashboard_routes.py     # API REST dashboard
│   ├── static/
│   │   ├── css/main.css        # Sistema de diseño completo
│   │   ├── js/main.js          # Interactividad del cliente
│   │   └── favicon.png
│   └── templates/
│       ├── base.html           # Layout base con sidebar
│       ├── index.html          # Página de inicio
│       ├── dashboard.html      # Panel de KPIs y gráficas
│       ├── productos.html      # CRUD productos
│       ├── proveedores.html    # CRUD proveedores
│       ├── ventas.html         # CRUD ventas
│       ├── optimizacion.html   # Resultados EOQ
│       ├── editar_producto.html
│       ├── editar_proveedor.html
│       ├── editar_venta.html
│       └── macros/
│           ├── forms.html      # Macros de formularios
│           ├── modals.html     # Macro de modales
│           ├── tables.html     # Macro de tablas ordenables
│           └── pagination.html # Macro de paginación
├── tests/
│   ├── test_api.py             # Tests de integración API
│   ├── test_math.py            # Tests del motor EOQ
│   └── test_models.py          # Tests de validación de modelos
├── docs/                       # Documentación y diagramas
├── main.py                     # Punto de entrada de la aplicación
├── Dockerfile                  # Configuración para producción
├── pyproject.toml              # Dependencias y metadatos
└── .env.example                # Ejemplo de variables de entorno
```

---

## Instalación y configuración

### Prerrequisitos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias)
- PostgreSQL
- Supabase para almacenamiento de imágenes

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/DevCris80/Proyecto-DEV-2026-1.git
cd Proyecto-DEV-2026-1

# 2. Crear archivo de variables de entorno
cp .env.example .env
```

Editar `.env` con los valores correspondientes:

```env
DATABASE_URL=postgresql+asyncpg://usuario:password@ep-tu-instancia.neon.tech/neondb
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-supabase
SUPABASE_BUCKET=nombre-de-tu-bucket
```

```bash
# 3. Instalar dependencias
uv sync

# 4. Ejecutar la aplicación
uv run uvicorn main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`.

### Poblar la base de datos con datos de prueba

```bash
uv run -m scripts.seed_data
```

---

## Despliegue con Docker

```bash
# Construir la imagen
docker build -t sispro .

# Ejecutar el contenedor
docker run -d -p 8000:8000 --env-file .env sispro
```

El `Dockerfile` usa una imagen slim con Python 3.11, instala dependencias con `uv --locked`, compila bytecode y ejecuta la aplicación con un usuario no root.

La aplicación ya se encuentra desplegada en **Render** en la URL:

[https://proyecto-dev-2026-1-1.onrender.com](https://proyecto-dev-2026-1-1.onrender.com)

---

## Modelo de datos

### Proveedor (`proveedores`)

| Campo                          | Tipo     | Descripción                              |
| ------------------------------ | -------- | ---------------------------------------- |
| `id`                           | UUID     | Identificador único                      |
| `nombre`                       | Texto    | Nombre del proveedor                     |
| `costo_pedido_fijo`            | Decimal  | Costo fijo por pedido                    |
| `lead_time_promedio`           | Decimal  | Tiempo de entrega promedio (días)        |
| `desviacion_estandar_lead_time`| Decimal  | Desviación estándar del lead time        |
| `nivel_servicio_objetivo`      | Decimal  | Nivel de servicio objetivo (0.8 – 0.99) |
| `imagen_url`                   | Texto    | URL del logo                             |
| `estado_activo`                | Booleano | Eliminación lógica                       |

### Producto (`productos`)

| Campo                         | Tipo     | Descripción                           |
| ----------------------------- | -------- | ------------------------------------- |
| `id`                          | UUID     | Identificador único                   |
| `nombre`                      | Texto    | Nombre del producto                   |
| `id_proveedor`                | UUID     | Relación muchos a uno con proveedor   |
| `stock_actual`                | Entero   | Cantidad disponible en inventario     |
| `costo_unitario`              | Decimal  | Costo por unidad                      |
| `costo_almacenamiento_anual`  | Decimal  | Costo anual de almacenamiento por ud. |
| `demanda_anual_estimada`      | Decimal  | Demanda estimada por año              |
| `imagen_url`                  | Texto    | URL de la imagen del producto         |
| `estado_activo`               | Booleano | Eliminación lógica                    |

### Venta (`ventas`)

| Campo        | Tipo  | Descripción                          |
| ------------ | ----- | ------------------------------------ |
| `id`         | UUID  | Identificador único                  |
| `id_producto`| UUID  | Relación muchos a uno con producto   |
| `cantidad`   | Entero| Cantidad vendida                     |
| `fecha_venta`| Fecha | Fecha de la venta                    |

---

## API Endpoints

### Rutas SSR (Server-Side Rendering)

| Método | Ruta                              | Descripción                        |
| ------ | --------------------------------- | ---------------------------------- |
| GET    | `/`                               | Página de inicio                   |
| GET    | `/dashboard`                      | Dashboard con KPIs y gráficas      |
| GET    | `/productos`                      | Listado de productos (paginado)    |
| POST   | `/productos`                      | Crear producto (formulario)        |
| GET    | `/productos/{id}/editar`          | Formulario de edición de producto  |
| POST   | `/productos/{id}/editar`          | Actualizar producto                |
| POST   | `/productos/{id}/delete`          | Eliminar producto (soft delete)    |
| GET    | `/proveedores`                    | Listado de proveedores (paginado)  |
| POST   | `/proveedores`                    | Crear proveedor (formulario)       |
| GET    | `/proveedores/{id}/editar`        | Formulario de edición de proveedor |
| POST   | `/proveedores/{id}/editar`        | Actualizar proveedor               |
| POST   | `/proveedores/{id}/delete`        | Eliminar proveedor (soft delete)   |
| GET    | `/ventas`                         | Listado de ventas (paginado)       |
| POST   | `/ventas`                         | Crear venta (formulario)           |
| GET    | `/ventas/{id}/editar`             | Formulario de edición de venta     |
| POST   | `/ventas/{id}/editar`             | Actualizar venta                   |
| POST   | `/ventas/{id}/delete`             | Eliminar venta                     |
| GET    | `/optimizacion`                   | Página de resultados EOQ           |

### API REST

Prefijo base: `http://localhost:8000`

#### Productos

| Método | Ruta                          | Descripción                             |
| ------ | ----------------------------- | --------------------------------------- |
| POST   | `/productos`                  | Crear producto (JSON)                   |
| GET    | `/productos`                  | Listar productos (filtro `?estado=`)    |
| GET    | `/productos/buscar?nombre=`   | Buscar productos por nombre             |
| PATCH  | `/productos/{id}`             | Actualizar producto parcialmente        |
| POST   | `/productos/{id}/imagen`      | Subir imagen del producto a Supabase    |
| DELETE | `/productos/{id}`             | Eliminar producto (soft delete)         |

#### Proveedores

| Método | Ruta                          | Descripción                             |
| ------ | ----------------------------- | --------------------------------------- |
| POST   | `/proveedores`                | Crear proveedor (JSON)                  |
| GET    | `/proveedores`                | Listar proveedores activos              |
| PATCH  | `/proveedores/{id}`           | Actualizar proveedor parcialmente       |
| POST   | `/proveedores/{id}/imagen`    | Subir logo a Supabase                   |
| DELETE | `/proveedores/{id}`           | Eliminar proveedor (soft delete)        |

#### Ventas

| Método | Ruta           | Descripción                                    |
| ------ | -------------- | ---------------------------------------------- |
| POST   | `/ventas`      | Registrar venta (descuesta stock automáticamente) |
| GET    | `/ventas`      | Listar ventas                                  |

#### Optimización EOQ

| Método | Ruta                        | Descripción                                    |
| ------ | --------------------------- | ---------------------------------------------- |
| GET    | `/optimizar/pedidos`        | Alertas de pedido no óptimas (caché 60s)       |
| GET    | `/optimizar/{id_producto}`  | Sugerencia EOQ para un producto específico     |

#### Dashboard

| Método | Ruta                  | Descripción                                    |
| ------ | --------------------- | ---------------------------------------------- |
| GET    | `/dashboard/resumen`  | Resumen: totales, ventas mensuales, stock      |

---

## Pruebas

```bash
uv run pytest
```

El proyecto incluye:
- **Tests de integración de API** (`tests/test_api.py`) — prueba los endpoints REST con un cliente HTTP asíncrono
- **Tests del motor EOQ** (`tests/test_math.py`) — verifica cálculos de EOQ, punto de reorden, stock de seguridad y niveles de alerta
- **Tests de modelos** (`tests/test_models.py`) — valida restricciones y schemas de Pydantic
