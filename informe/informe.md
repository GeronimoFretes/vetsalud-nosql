# Trabajo Práctico Obligatorio

# Sistema de Gestión de Clínica Veterinaria VetSalud

**Materia:** Bases de Datos II
**Proyecto:** Sistema de Gestión de Clínica Veterinaria 
**Repositorio:** https://github.com/GeronimoFretes/vetsalud-nosql

---

## 1. Introducción

El objetivo del trabajo fue diseñar e implementar una solución de persistencia NoSQL para VetSalud S.A., una clínica veterinaria que busca reemplazar el uso de planillas por una arquitectura de datos más organizada, reproducible y escalable.

La solución implementada utiliza persistencia políglota, combinando dos motores NoSQL de paradigmas diferentes. MongoDB se utiliza como base documental principal para la información clínica y administrativa, mientras que Redis se utiliza para el manejo del stock farmacéutico.

El proyecto incluye la carga de datos desde los archivos CSV provistos, la incorporación de registros adicionales, la implementación de los 15 servicios solicitados y la generación de salidas JSON para documentar los resultados.

---

## 2. Arquitectura elegida

La arquitectura utiliza dos motores NoSQL.

MongoDB almacena las siguientes colecciones.

```text
propietarios
pacientes
veterinarios
consultas
vacunaciones
cirugias
```

Redis almacena el stock farmacéutico mediante hashes, sorted sets y una lista de movimientos.

```text
stock:producto:<id_producto>
idx:stock:unidades
movimientos:stock
```

La decisión busca asignar cada parte del dominio al motor que mejor responde a sus patrones de acceso. MongoDB se adapta mejor a los datos clínicos y administrativos, donde se necesitan consultas por múltiples campos, agregaciones, filtros por fecha y relaciones por referencia. Redis se adapta mejor al stock, donde se necesitan accesos rápidos por clave, actualización de cantidades y consulta eficiente de productos con bajo stock.

---

## 3. Justificación técnica de los motores

### 3.1. MongoDB

MongoDB fue elegido como motor principal porque el dominio clínico de VetSalud contiene entidades con estructura flexible y relaciones frecuentes entre documentos. Las consultas requeridas combinan pacientes, propietarios, veterinarios, consultas y vacunaciones. Para resolverlas se utilizan operaciones de filtrado, agregación y `$lookup`.

Se eligió un modelo principalmente referenciado. Por ejemplo, cada paciente guarda el `id_propietario`, cada consulta guarda el `id_paciente` y el `id_vet`, y cada vacunación guarda el paciente y el veterinario asociados.

Esta decisión evita duplicar información sensible o mutable. Por ejemplo, si los datos de un propietario cambian, se actualiza un único documento en la colección `propietarios`. Esto es especialmente importante porque el trabajo exige un ABM completo de propietarios con modificación de datos y baja lógica.

Se descartó un modelo fuertemente embebido porque habría generado duplicación de propietarios, veterinarios o historias clínicas dentro de otros documentos. Aunque el embedding puede ser útil cuando los datos se consultan siempre juntos, en este caso las entidades también se consultan de forma independiente.

### 3.2. Redis

Redis fue elegido para el stock farmacéutico. Cada producto se guarda como un hash y sus unidades disponibles se indexan en un sorted set. Esto permite resolver directamente la consulta de productos con menos de 50 unidades.

Cada producto se modela así.

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

El índice de unidades se modela así.

```text
idx:stock:unidades
  member = id_producto
  score = unidades
```

Esta estructura permite consultar productos con bajo stock mediante `ZRANGEBYSCORE` y luego recuperar los datos completos con `HGETALL`.

También se implementó una actualización masiva de stock después de una consulta. La actualización decrementa las unidades del hash, actualiza el sorted set y registra el movimiento en una lista de Redis. Esto muestra que Redis no se usa como un simple cache, sino como motor persistente para un caso funcional específico.

---

## 4. Modelo de datos

### 4.1. Colección propietarios

Cada propietario contiene datos de identificación y contacto. Además se incorpora el campo `activo`, necesario para implementar la baja lógica.

Campos principales.

```text
id_propietario
nombre
apellido
dni
email
telefono
ciudad
provincia
activo
```

### 4.2. Colección pacientes

Cada paciente representa un animal registrado en la clínica.

Campos principales.

```text
id_paciente
nombre
especie
raza
fecha_nac
id_propietario
activo
```

La relación con propietarios se resuelve mediante `id_propietario`.

### 4.3. Colección veterinarios

Cada veterinario contiene datos profesionales, especialidad, sucursal y estado activo.

Campos principales.

```text
id_vet
nombre
apellido
matricula
especialidad
sucursal
activo
```

### 4.4. Colección consultas

Cada consulta médica referencia a un paciente y a un veterinario.

Campos principales.

```text
id_consulta
id_paciente
id_vet
fecha
motivo
tipo_consulta
diagnostico
costo
estado
```

El campo `tipo_consulta` se deriva durante la carga de datos a partir del campo `motivo`. Esto permite resolver de forma más clara la consulta de controles con costo menor a 5000.

### 4.5. Colección vacunaciones

Cada vacunación referencia a un paciente y a un veterinario.

Campos principales.

```text
id_vacuna
id_paciente
id_vet
fecha_aplicacion
nombre_vacuna
proxima_dosis
```

El campo `proxima_dosis` permite detectar vacunas vencidas.

### 4.6. Colección cirugías

Se agregó una colección de cirugías para cubrir el dominio funcional mencionado en el enunciado. Aunque no hay un servicio específico asociado a cirugías, la colección completa el modelo clínico.

Campos principales.

```text
id_cirugia
id_paciente
id_vet
fecha
tipo
resultado
costo
```

### 4.7. Stock farmacéutico en Redis

El stock se separa del modelo clínico y se almacena en Redis. Se utilizan tres estructuras.

```text
stock:producto:<id_producto>
idx:stock:unidades
movimientos:stock
```

La primera guarda los datos completos del producto, la segunda permite buscar por cantidad disponible y la tercera registra movimientos de stock.

---

## 5. Carga de datos

La carga de datos se realiza mediante scripts reproducibles. Los archivos CSV originales se ubican en `data/raw/` y se importan con los scripts del módulo `src.seed`.

El comando principal de carga es el siguiente.

```bash
python -m src.seed.seed_all
```

Durante la carga se normalizan tipos de datos. Las fechas se convierten a objetos de fecha, los costos y precios a valores numéricos, y los campos booleanos a valores lógicos. También se agregan registros adicionales para cumplir con el requisito de incorporar al menos 10 registros propios por colección o tabla.

Los registros adicionales fueron diseñados para asegurar que los servicios devuelvan resultados significativos. Se incorporaron propietarios con más de un paciente, consultas recientes, consultas en seguimiento, controles con costo menor a 5000, vacunas vencidas, productos con bajo stock y movimientos posibles de stock.

---

## 6. Servicios implementados

Los 15 servicios fueron implementados en módulos separados dentro de `src/services/`. Cada servicio genera una salida JSON en la carpeta `outputs/`.

| Nº | Servicio                                                  | Motor   |
| -: | --------------------------------------------------------- | ------- |
|  1 | Pacientes activos con datos de propietario                | MongoDB |
|  2 | Consultas en seguimiento con veterinario asignado y costo | MongoDB |
|  3 | Historial completo de paciente                            | MongoDB |
|  4 | Propietarios con más de un paciente                       | MongoDB |
|  5 | Veterinarios activos y consultas en últimos 60 días       | MongoDB |
|  6 | Pacientes con vacunas vencidas                            | MongoDB |
|  7 | Top 5 diagnósticos más frecuentes                         | MongoDB |
|  8 | Stock menor a 50 unidades con proveedor                   | Redis   |
|  9 | Consultas tipo Control con costo menor a 5000             | MongoDB |
| 10 | Pacientes por sucursal a través del veterinario           | MongoDB |
| 11 | Ingresos totales por veterinario en el mes actual         | MongoDB |
| 12 | Propietarios sin consultas en el último año               | MongoDB |
| 13 | ABM completo de propietarios                              | MongoDB |
| 14 | Registro de nueva consulta con validación                 | MongoDB |
| 15 | Actualización masiva de stock tras consulta               | Redis   |

### Servicio 1

El servicio obtiene pacientes activos junto con los datos completos de su propietario. Se utiliza `$match` para filtrar pacientes activos y `$lookup` para incorporar la información del propietario.

Archivo de salida.

```text
outputs/service_01_pacientes_activos.json
```

### Servicio 2

El servicio obtiene consultas en estado `Seguimiento`, incluyendo veterinario asignado, paciente y costo. Se utilizan `$lookup` sobre `veterinarios` y `pacientes`.

Archivo de salida.

```text
outputs/service_02_consultas_seguimiento.json
```

### Servicio 3

El servicio genera el historial completo de un paciente, combinando consultas y vacunaciones. La información se normaliza en una lista de eventos y se ordena por fecha.

Archivo de salida.

```text
outputs/service_03_historial_paciente.json
```

### Servicio 4

El servicio identifica propietarios con más de un paciente registrado. Se utiliza `$group` para contar pacientes por propietario y `$lookup` para recuperar los datos del propietario.

Archivo de salida.

```text
outputs/service_04_propietarios_multiples_pacientes.json
```

### Servicio 5

El servicio lista veterinarios activos y cuenta sus consultas en los últimos 60 días. Se parte de la colección `veterinarios`, lo que permite incluir también veterinarios activos con cero consultas recientes.

Archivo de salida.

```text
outputs/service_05_veterinarios_consultas_60_dias.json
```

### Servicio 6

El servicio detecta pacientes con vacunas vencidas. Se filtran vacunaciones cuya `proxima_dosis` es anterior a la fecha actual y se agregan datos de paciente y veterinario.

Archivo de salida.

```text
outputs/service_06_vacunas_vencidas.json
```

### Servicio 7

El servicio calcula los cinco diagnósticos más frecuentes. Se agrupan las consultas por diagnóstico, se cuenta la cantidad de apariciones y se ordena de mayor a menor.

Archivo de salida.

```text
outputs/service_07_top_diagnosticos.json
```

### Servicio 8

El servicio consulta Redis para obtener productos con menos de 50 unidades. Usa el sorted set `idx:stock:unidades` para identificar productos y luego recupera sus datos completos desde los hashes de producto.

Archivo de salida.

```text
outputs/service_08_stock_bajo.json
```

### Servicio 9

El servicio obtiene consultas de tipo `Control` con costo menor a 5000. El campo `tipo_consulta` se genera durante la carga de datos para evitar depender de búsquedas sobre texto libre.

Archivo de salida.

```text
outputs/service_09_controles_bajo_costo.json
```

### Servicio 10

El servicio obtiene pacientes asociados a una sucursal determinada a través del veterinario que los atendió. El recorrido es consultas, veterinarios y pacientes.

Archivo de salida.

```text
outputs/service_10_pacientes_por_sucursal.json
```

### Servicio 11

El servicio calcula ingresos totales por veterinario en el mes actual. Se filtran consultas por rango de fechas y se agrupan por veterinario, sumando el costo de las consultas.

Archivo de salida.

```text
outputs/service_11_ingresos_mes_actual.json
```

### Servicio 12

El servicio identifica propietarios sin consultas registradas en el último año. Se parte de propietarios, se buscan sus pacientes y luego se verifica la ausencia de consultas recientes.

Archivo de salida.

```text
outputs/service_12_propietarios_sin_consultas_anio.json
```

### Servicio 13

El servicio implementa el ABM completo de propietarios. Incluye alta, modificación de datos y baja lógica. La baja lógica conserva el documento y actualiza `activo=false`.

Archivo de salida.

```text
outputs/service_13_abm_propietarios.json
```

### Servicio 14

El servicio registra una nueva consulta médica validando que el paciente y el veterinario existan y estén activos. Esta validación es necesaria porque MongoDB no impone claves foráneas automáticamente.

Archivo de salida.

```text
outputs/service_14_registrar_consulta.json
```

### Servicio 15

El servicio actualiza stock en Redis después de una consulta. Decrementa las unidades consumidas, actualiza el sorted set de unidades disponibles y registra el movimiento de stock.

Archivo de salida.

```text
outputs/service_15_actualizar_stock.json
```

Los resultados resumidos de cada servicio se presentan en la sección siguiente.

---

## 7. Resultados de ejemplo

A continuación se presenta un resultado resumido por cada servicio implementado. Las salidas completas se encuentran en la carpeta `outputs/` en formato JSON.

| Nº | Resultado de ejemplo |
|---:|---|
| 1 | Paciente `P008`: Bambú (Ave, Cacatúa), propietario Tomás Juárez. |
| 2 | Consulta `CEX003` en estado `Seguimiento`, paciente Luna, veterinario Camila Ojeda, costo $4.900,00. |
| 3 | Paciente `PEX001`: Mora. Primeros eventos del historial: vacunacion 2025-05-07, consulta 2026-06-01, consulta 2026-06-06. |
| 4 | Propietario `C001`: Ana Rodríguez, 2 pacientes registrados. |
| 5 | Veterinario `VEX005`: Julieta Campos, 1 consultas en los últimos 60 días. |
| 6 | Vacuna `Antirrabica` vencida para Olivia (`PEX009`), próxima dosis 2025-10-14. |
| 7 | Diagnóstico más frecuente: `Sano`, 5 consultas. |
| 8 | Producto `PRX006`: Anestesico, 15 unidades, proveedor VetSur. |
| 9 | Consulta `CON007` de tipo `Control`, costo $2.000,00. |
| 10 | Paciente `P001`: Firulais, sucursal consultada Palermo, 2 consulta/s. |
| 11 | Veterinario `VEX004`: Esteban Molina, ingresos del mes $8.800,00 en 1 consulta/s. |
| 12 | Propietario `PRA009`: Valentina Castro, 0 paciente/s y sin consultas en el último año. |
| 13 | Se creó el propietario `PABM001` y luego se aplicó baja lógica. Estado final: activo=False. |
| 14 | Consulta `CNUEVA001` registrada para Mora con veterinario Ana Pereyra. |
| 15 | Consulta `CNUEVA001`: producto `PRX003` decrementado de 120 a 118 unidades. |

---

## 8. Ejecución y reproducibilidad

El proyecto puede ejecutarse desde cero con los siguientes comandos.

```bash
docker compose up -d
python -m pip install -r requirements.txt
cp .env.example .env
python -m src.run_all_services --reset
python -m src.validate_project
```

El comando `run_all_services --reset` reconstruye las bases desde los CSV y los datos adicionales, ejecuta los 15 servicios y genera las salidas JSON. El comando `validate_project` verifica que las colecciones tengan datos suficientes, que Redis tenga stock cargado, que existan las salidas de los servicios y que los 15 servicios hayan finalizado correctamente.

La validación genera el archivo.

```text
outputs/validation_summary.json
```

---

## 9. Conclusión

La solución implementa una arquitectura NoSQL políglota para VetSalud, utilizando MongoDB y Redis con responsabilidades diferenciadas.

MongoDB concentra el dominio clínico y administrativo, resolviendo consultas sobre pacientes, propietarios, veterinarios, consultas y vacunaciones. Redis concentra el dominio de stock farmacéutico, resolviendo consultas de bajo stock y actualizaciones de unidades disponibles.

El proyecto cumple con la carga de datos desde CSV, la incorporación de registros adicionales, la implementación de los 15 servicios requeridos, la generación de resultados y la validación reproducible del sistema.

---

## 10. Bibliografía

Corbellini, A., Mateos, C., Zunino, A., Godoy, D. y Schiaffino, S. (2017). *Persisting big-data: The NoSQL landscape*.

Perkins, L., Redmond, E. y Wilson, J. R. (2018). *Seven Databases in Seven Weeks: A Guide to Modern Databases and the NoSQL Movement*. Segunda edición.

Date, C. J. (2003). *An Introduction to Database Systems*. Octava edición.
