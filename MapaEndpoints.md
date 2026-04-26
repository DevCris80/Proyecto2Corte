# Mapa de Endpoints

## Proveedores
| Método | Endpoint | Descripción |
|--------|----------|--------------|
| POST | `/proveedores` | Crear un nuevo proveedor |
| GET | `/proveedores` | Listar todos los proveedores activos |
| PATCH | `/proveedores/{id}` | Actualizar un proveedor por ID |
| DELETE | `/proveedores/{id}` | Eliminar (desactivar) un proveedor por ID |

## Productos
| Método | Endpoint | Descripción |
|--------|----------|--------------|
| POST | `/productos` | Crear un nuevo producto |
| GET | `/productos` | Listar productos (opcional: `?estado=true/false`) |
| GET | `/productos/buscar/?nombre=...` | Buscar productos por nombre |
| PATCH | `/productos/{id}` | Actualizar un producto por ID |
| DELETE | `/productos/{id}` | Eliminar (desactivar) un producto por ID |

## Ventas
| Método | Endpoint | Descripción |
|--------|----------|--------------|
| POST | `/ventas` | Registrar una venta |
| GET | `/ventas` | Listar todas las ventas |

## Optimización (Motor Matemático)
| Método | Endpoint | Descripción |
|--------|----------|--------------|
| GET | `/optimizar/pedidos` | Obtener alertas de pedidos para todos los productos |
| GET | `/optimizar/{id_producto}` | Obtener sugerencia de pedido para un producto específico |

## Raíz
| Método | Endpoint | Descripción |
|--------|----------|--------------|
| GET | `/` | Mensaje de bienvenida |