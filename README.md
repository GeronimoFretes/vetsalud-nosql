# VetSalud NoSQL

Trabajo Práctico Obligatorio de Bases de Datos II.

El proyecto implementa una arquitectura de persistencia políglota para un sistema de gestión de clínica veterinaria. La solución migra datos desde archivos CSV hacia dos motores NoSQL de paradigmas diferentes.

## Arquitectura

Se utilizan dos motores NoSQL:

- MongoDB como base documental principal para propietarios, pacientes, veterinarios, consultas, vacunaciones y cirugías.
- Redis como base clave-valor / estructuras de datos para stock farmacéutico.

La decisión busca asignar cada parte del dominio al motor que mejor se adapta a sus patrones de acceso.

MongoDB se usa para datos clínicos y administrativos, donde se requieren filtros, agregaciones, relaciones por referencia y consultas históricas.

Redis se usa para stock farmacéutico, donde se requieren accesos por clave, consultas rápidas de bajo stock y actualizaciones de unidades.

## Tecnologías

- Python
- MongoDB
- Redis
- Docker Compose

## Estructura del proyecto

```text
data/raw/         CSVs originales provistos por la cátedra
src/db/           Conexiones a MongoDB y Redis
src/seed/         Scripts de carga de datos
src/services/     Servicios requeridos por el enunciado
src/utils/        Utilidades comunes
outputs/          Salidas JSON generadas por los servicios
informe/          Informe final
```

## Requisitos

Tener instalado:

- Docker
- Docker Compose
- Python 3.11 o superior

## Configuración inicial

Levantar MongoDB y Redis:

```bash
docker compose up -d
```

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

Crear archivo de entorno local:

```bash
cp .env.example .env
```

Verificar conexiones:

```bash
python -m src.check_connections
```

## Carga de datos

La carga de datos importa los CSV originales, normaliza tipos de datos y agrega registros adicionales para cubrir los servicios requeridos.

```bash
python -m src.seed.seed_all
```

Verificar carga:

```bash
python -m src.seed.check_seed
```

## Ejecutar servicios

Listar servicios disponibles:

```bash
python -m src.run_service --list
```

Ejecutar un servicio individual:

```bash
python -m src.run_service 8
```

Ejecutar todos los servicios:

```bash
python -m src.run_all_services
```

Reconstruir las bases desde cero y ejecutar todos los servicios:

```bash
python -m src.run_all_services --reset
```

Las salidas de ejemplo se guardan en la carpeta `outputs/`.

## Validar el proyecto

Después de ejecutar todos los servicios, correr:

```bash
python -m src.validate_project
```

Este comando valida:

- cantidad mínima de registros en MongoDB
- existencia de stock en Redis
- funcionamiento del índice de bajo stock
- existencia de salidas JSON para los 15 servicios
- ejecución correcta de todos los servicios
- casos de negocio necesarios para que las consultas devuelvan resultados significativos

## Servicios implementados

| Nº | Servicio | Motor |
|---:|---|---|
| 1 | Pacientes activos con datos de propietario | MongoDB |
| 2 | Consultas en seguimiento con veterinario asignado y costo | MongoDB |
| 3 | Historial completo de paciente | MongoDB |
| 4 | Propietarios con más de un paciente | MongoDB |
| 5 | Veterinarios activos y consultas en últimos 60 días | MongoDB |
| 6 | Pacientes con vacunas vencidas | MongoDB |
| 7 | Top 5 diagnósticos más frecuentes | MongoDB |
| 8 | Stock menor a 50 unidades con proveedor | Redis |
| 9 | Consultas tipo Control con costo menor a 5000 | MongoDB |
| 10 | Pacientes por sucursal a través del veterinario | MongoDB |
| 11 | Ingresos totales por veterinario en el mes actual | MongoDB |
| 12 | Propietarios sin consultas en el último año | MongoDB |
| 13 | ABM completo de propietarios | MongoDB |
| 14 | Registro de nueva consulta con validación | MongoDB |
| 15 | Actualización masiva de stock tras consulta | Redis |

## Modelo de datos

### MongoDB

Colecciones:

- `propietarios`
- `pacientes`
- `veterinarios`
- `consultas`
- `vacunaciones`
- `cirugias`

Se utiliza un modelo principalmente referenciado. Por ejemplo:

- `pacientes.id_propietario` referencia a `propietarios.id_propietario`
- `consultas.id_paciente` referencia a `pacientes.id_paciente`
- `consultas.id_vet` referencia a `veterinarios.id_vet`
- `vacunaciones.id_paciente` referencia a `pacientes.id_paciente`
- `vacunaciones.id_vet` referencia a `veterinarios.id_vet`

Esta decisión evita duplicación excesiva y facilita operaciones como el ABM de propietarios.

### Redis

Estructuras:

```text
stock:producto:<id_producto>
idx:stock:unidades
movimientos:stock
```

Cada producto se guarda como hash:

```text
stock:producto:PRX001
  id_producto
  nombre
  categoria
  unidades
  precio_unit
  vencimiento
  proveedor
```

El índice de unidades se guarda como sorted set:

```text
idx:stock:unidades
  member = id_producto
  score = unidades
```

Esto permite consultar productos con menos de 50 unidades de forma directa.

## Comando recomendado para corrección

Para reconstruir todo desde cero, ejecutar servicios y validar:

```bash
python -m src.run_all_services --reset
python -m src.validate_project
```

Si ambos comandos finalizan correctamente, el proyecto queda cargado, ejecutado y validado.