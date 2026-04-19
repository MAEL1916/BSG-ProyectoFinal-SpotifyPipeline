# RUNBOOK - Pipeline Spotify Analytics

##  Información General

**Pipeline:** Spotify Analytics ETL  
**Proveedor Cloud:** Microsoft Azure  
**Frecuencia de ejecución:** Manual
**Owner:** Elias Martinez

---

##  Ejecución Normal

### Opción 1: Usar Makefile

```bash
# Activar entorno y ejecutar
make run
```

### Opción 2: Ejecución directa

```bash
# Desde la raíz del proyecto
python src/main.py
```

### Salida Esperada

```
2026-04-19 10:30:15 - INFO - Iniciando APi Spotify
2026-04-19 10:30:16 - INFO - --- PASO 1: EXTRACCIÓN ---
2026-04-19 10:30:17 - INFO - Descargando spotify_wrapped_2025.csv desde spotify-data
2026-04-19 10:30:18 - INFO - Archivo descargado: 1543 registros
2026-04-19 10:30:19 - INFO - Conectando a Deezer API
2026-04-19 10:30:22 - INFO - Datos de Deezer API obtenidos: 50 registros
2026-04-19 10:30:23 - INFO - --- PASO 2: TRANSFORMACIÓN BRONZE ---
2026-04-19 10:30:24 - INFO - Capa Bronze creada: 1593 registros
2026-04-19 10:30:25 - INFO - --- PASO 3: TRANSFORMACIÓN SILVER ---
2026-04-19 10:30:26 - INFO - Capa Silver creada: 1589 registros
2026-04-19 10:30:27 - INFO - --- PASO 4: TRANSFORMACIÓN GOLD ---
2026-04-19 10:30:28 - INFO - Capa Gold creada: 120 artistas únicos
2026-04-19 10:30:29 - INFO - --- PASO 5: CARGA A AZURE ---
2026-04-19 10:30:32 - INFO - Datos Bronze guardados en bronze/spotify/ingestion_date=2026-04-19/datos.parquet
2026-04-19 10:30:35 - INFO - Datos Silver guardados en silver/spotify/event_date=2026-04-19/datos.parquet
2026-04-19 10:30:38 - INFO - Datos Gold guardados en gold/spotify/metricas_artistas.parquet
2026-04-19 10:30:39 - INFO - === PIPELINE COMPLETADO EXITOSAMENTE ===
2026-04-19 10:30:39 - INFO - Bronze: 1593 registros
2026-04-19 10:30:39 - INFO - Silver: 1589 registros
2026-04-19 10:30:39 - INFO - Gold: 120 artistas
2026-04-19 10:30:39 - INFO - Pipeline ejecutado correctamente
```

**Exit code:** `0` (éxito) o `1` (error)

---

##  Re-ejecución del Pipeline

### Escenario 1: Ejecución completa desde cero

```bash
# Los datos se sobrescriben automáticamente (overwrite=True)
make run
```

**Impacto:**
- Los archivos Parquet del día actual se reemplazan
- No afecta datos de fechas anteriores (particionado)

### Escenario 2: Solo probar sin escribir a Azure

```bash
# Comentar temporalmente las funciones de carga en main.py
# O crear variable de entorno DRY_RUN=true (requiere modificación del código)
```

---

##  Backfill (Carga Histórica)

### ¿Qué es un backfill?

Re-procesar datos de fechas pasadas para llenar huecos o corregir errores.

### Cómo hacer backfill manual

**1. Modificar timestamp en transform.py:**

```python
# En crear_bronze()
# Cambiar:
datos_completos['ingestion_timestamp'] = datetime.now()

# Por:
from datetime import datetime, timedelta
fecha_backfill = datetime.now() - timedelta(days=7)  # 7 días atrás
datos_completos['ingestion_timestamp'] = fecha_backfill
```

**2. Ejecutar pipeline:**

```bash
make run
```

**3. Revertir cambios:**

Volver a poner `datetime.now()` para ejecuciones futuras.

### Backfill automatizado (futuro)

```bash
# Pasar fecha como argumento
python src/main.py --backfill-date 2026-04-10
```

---

##  Troubleshooting - Qué Revisar Si Falla

### Error 1: "Error al descargar CSV"

**Mensaje:**
```
ERROR - Error en dwspotify: No se pudo conectar a Azure
ERROR - Error al descargar CSV
```

**Causas probables:**
1. Credenciales de Azure Blob incorrectas
2. Contenedor o blob no existe
3. Sin conexión a internet

**Solución:**

```bash
# 1. Verificar variables de entorno
cat .env | grep AZURE

# 2. Verificar que existan:
# CONEXION_AZURE=DefaultEndpointsProtocol=https;AccountName=...
# AZURE_CONTAINER_NAME=nombre-contenedor
# AZURE_BLOB_NAME=spotify_wrapped_2025.csv

# 3. Probar conexión manual
python -c "
from utils.conexion import conectar_azure_blob
blob_service = conectar_azure_blob()
print('Conectado:', blob_service is not None)
"

# 4. Listar contenedores disponibles
python -c "
from utils.conexion import conectar_azure_blob
blob = conectar_azure_blob()
containers = list(blob.list_containers())
print('Contenedores:', [c.name for c in containers])
"
```

---

### Error 2: "API no disponible"

**Mensaje:**
```
WARNING - API no disponible
INFO - Continuando solo con CSV
```

**Impacto:** Pipeline continúa (degradación graceful), pero solo procesa datos del CSV.

**Causas probables:**
1. Deezer API caída temporalmente
2. Timeout de red (>10 segundos)
3. Rate limiting

**Solución:**
- Si es aceptable: Ignorar (pipeline funciona solo con CSV)
- Si se requiere API: Esperar 5-10 minutos y re-ejecutar

**Verificar manualmente:**
```bash
curl https://api.deezer.com/artist/75491
# Debe retornar JSON con info de Eminem
```

---

### Error 3: "Validación Bronze/Silver/Gold falló"

**Mensaje:**
```
ERROR - Validación Bronze falló
ERROR - Pipeline falló
```

**Causas probables:**
1. Esquema del CSV cambió (nuevas columnas, columnas faltantes)
2. Tipos de datos incorrectos
3. Valores nulos en campos obligatorios

**Solución:**

```bash
# 1. Ver qué falló exactamente (revisar logs anteriores)
# Buscar líneas con "ValidationError"

# 2. Inspeccionar el DataFrame antes de validar
# Agregar en main.py temporalmente:
print(datos_bronze.columns)
print(datos_bronze.dtypes)
print(datos_bronze.head())

# 3. Actualizar schema JSON si el CSV cambió legítimamente
# Editar: data_contracts/schemas/bronze_schema.json
```

---

### Error 4: "Error al guardar Bronze/Silver/Gold"

**Mensaje:**
```
ERROR - Error en guardar_bronze: [mensaje específico]
ERROR - Error al guardar Bronze
```

**Causas probables:**
1. Credenciales de ADLS incorrectas
2. Container no existe
3. Permisos insuficientes
4. Quota de storage excedida

**Solución:**

```bash
# 1. Verificar credenciales ADLS
cat .env | grep ADLS

# 2. Debe tener:
# ADLS_ACCOUNT_NAME=nombre-cuenta
# ADLS_ACCOUNT_KEY=clave-acceso-larga
# ADLS_CONTAINER_NAME=nombre-contenedor

# 3. Probar conexión manual
python -c "
from pipeline.load import conectar_adls
client = conectar_adls()
print('Conectado:', client is not None)
"

# 4. Verificar permisos del container
# Ir a Azure Portal → Storage Account → Access Control (IAM)
# Debe tener rol: Storage Blob Data Contributor
```

---

### Error 5: Pipeline se cuelga (no responde)

**Síntoma:** El comando `make run` no termina después de varios minutos.

**Causas probables:**
1. API Deezer muy lenta (timeout no configurado correctamente)
2. CSV muy grande (>100MB)
3. Problema de red intermitente

**Solución:**

```bash
# 1. Cancelar con Ctrl+C

# 2. Verificar timeout de API en extract.py
# Debe tener: timeout=10 en requests.get()

# 3. Verificar tamaño del CSV
ls -lh [ruta-al-csv-local-si-está-descargado]

# 4. Ejecutar con más logging
python src/main.py 2>&1 | tee pipeline.log
```

---

##  Logs - Dónde Mirar

### Logs en tiempo real

```bash
# Ejecutar con salida en consola
make run

# Guardar logs en archivo
make run 2>&1 | tee logs/$(date +%Y-%m-%d).log
```

### Logs en Azure (futuro)

**Azure Monitor:**
1. Portal Azure → Monitor → Logs
2. Query:
```kql
AzureDiagnostics
| where ResourceType == "DATALAKESTORE"
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
```

### Niveles de log importantes

| Nivel | Qué significa | Acción requerida |
|-------|---------------|------------------|
| `INFO` | Operación normal | Ninguna |
| `WARNING` | Degradación (ej: API caída) | Revisar si es aceptable |
| `ERROR` | Fallo crítico | Investigar inmediatamente |

---

##  Validación Post-Ejecución

### 1. Verificar que los archivos se crearon en Azure

**Portal Azure:**
1. Ir a Storage Account → Containers → [tu-contenedor]
2. Buscar rutas:
   - `bronze/spotify/ingestion_date=2026-04-19/datos.parquet`
   - `silver/spotify/event_date=2026-04-19/datos.parquet`
   - `gold/spotify/metricas_artistas.parquet`

**Azure CLI:**
```bash
az storage fs file list \
  --account-name <tu-cuenta> \
  --file-system <tu-contenedor> \
  --path "bronze/spotify/" \
  --auth-mode key
```

### 2. Verificar tamaño de archivos

```bash
# Los archivos Parquet deberían ser:
# Bronze: ~50-500KB (depende de registros)
# Silver: ~40-450KB (ligeramente menor)
# Gold: ~5-50KB (mucho menor por agregación)
```

### 3. Leer datos desde Azure (validación)

```python
# Script de validación
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient

service_client = DataLakeServiceClient(
    account_url="https://<cuenta>.dfs.core.windows.net",
    credential="<clave>"
)

# Leer Gold
file_client = service_client.get_file_system_client("<container>") \
    .get_file_client("gold/spotify/metricas_artistas.parquet")

with open("temp_gold.parquet", "wb") as f:
    data = file_client.download_file()
    f.write(data.readall())

df = pd.read_parquet("temp_gold.parquet")
print(df.head())
print(f"Total artistas: {len(df)}")
```

---

##  Alertas Recomendadas (futuro)

| Condición | Severidad | Acción |
|-----------|-----------|--------|
| Pipeline falla 2 veces consecutivas | Alta | Email + Slack |
| Tiempo de ejecución > 10 minutos | Media | Email |
| Bronze < 100 registros | Media | Investigar fuente |
| % pérdida Silver/Bronze > 15% | Alta | Revisar validaciones |
| Gold = 0 artistas | Crítica | Detener siguiente ejecución |

---
##  Rollback (Revertir Ejecución)

Si una ejecución generó datos incorrectos:

### 1. Borrar archivos del día actual

**Azure Portal:**
1. Storage Account → Containers → [contenedor]
2. Navegar a `bronze/spotify/ingestion_date=2026-04-19/`
3. Delete folder

**Azure CLI:**
```bash
az storage fs directory delete \
  --account-name <cuenta> \
  --file-system <contenedor> \
  --name "bronze/spotify/ingestion_date=2026-04-19" \
  --yes
```

### 2. Re-ejecutar pipeline

```bash
make run
```

---

##  Monitoreo de Métricas

### KPIs del Pipeline

```bash
# Extraer de logs después de ejecución
grep "Bronze:" pipeline.log  # Registros Bronze
grep "Silver:" pipeline.log  # Registros Silver  
grep "Gold:" pipeline.log    # Artistas Gold

# Calcular pérdida de datos
python -c "
bronze = 1593
silver = 1589
loss = ((bronze - silver) / bronze) * 100
print(f'Pérdida: {loss:.2f}%')
"
```

### Histórico de Ejecuciones

```bash
# Crear CSV con historial (agregar a cada ejecución)
echo "$(date '+%Y-%m-%d %H:%M:%S'),1593,1589,120,SUCCESS" >> logs/history.csv

# Columnas: fecha,bronze,silver,gold,status
```
