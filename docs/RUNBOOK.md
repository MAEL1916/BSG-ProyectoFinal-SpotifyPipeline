# RUNBOOK - Pipeline Spotify Analytics


## Cómo ejecutar el pipeline

**El pipeline corre de forma manual, tarda ~30 segundos, y sube todo a Azure Data Lake.** 

```bash
make run

python src/main.py
```

### Qué esperar

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

Si todo salió bien, exit code = 0.

---

## Re-ejecutar el pipeline

Para volver a correr el pipeline, simplemente `make run` otra vez. Los archivos del mismo día se sobrescriben (overwrite=True), pero fechas anteriores no se tocan por el particionado.

**Nota:** Si solo quieres probar sin escribir a Azure, comenta las funciones `guardar_*()` en main.py temporalmente.

---

### Error: "Error al descargar CSV"

```
ERROR - Error en dwspotify: No se pudo conectar a Azure
ERROR - Error al descargar CSV
```

**Causas:** Credenciales mal en .env, contenedor no existe, o sin internet.

**Cómo arreglarlo:**

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

### Error: "API no disponible"

**Mensaje:**
```
WARNING - API no disponible
INFO - Continuando solo con CSV
```

**Alerta:** El pipeline sigue corriendo (solo usa el CSV). Si necesitas los datos de API sí o sí, espera 5-10 min y vuelve a intentar.

Para verificar si Deezer está caído:
```bash
curl https://api.deezer.com/artist/75491
# Debe retornar JSON con info de Eminem
```

### Error: "Validación Bronze/Silver/Gold falló"
```
ERROR - Validación Bronze falló
ERROR - Pipeline falló
```

Esto pasa cuando el esquema del CSV cambió o hay datos malos.

**Qué hacer:**

```bash
# 1. Ver qué falló exactamente (revisar logs anteriores)
# Buscar líneas con "ValidationError"

# 2. Inspeccionar el DataFrame antes de validar
# Agregar en main.py temporalmente:
print(datos_bronze.columns)
print(datos_bronze.dtypes)
print(datos_bronze.head())

# 3. Si el CSV cambió de verdad, actualiza el schema JSON
nano data_contracts/schemas/bronze_schema.json
```

### Error: "Error al guardar a Azure"

**Mensaje:**
```
ERROR - Error en guardar_bronze: [mensaje específico]
ERROR - Error al guardar Bronze
```

**Causas comunes:** Credenciales ADLS mal, container no existe, o permisos.

**Fix:**

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

# 4. Revisar permisos en Azure Portal
# Storage Account → IAM → debe tener rol "Storage Blob Data Contributor"
```

---

## Logs

Los logs salen directo en consola cuando ejecutas `make run`. Si quieres guardarlos:

```bash
make run 2>&1 | tee logs/$(date +%Y-%m-%d).log
```

**INFO** = todo bien | **WARNING** = algo raro pero sigue | **ERROR** = se rompió

---

## Verificar que todo se subió bien

Después de ejecutar, revisa en Azure Portal que los archivos estén ahí:
- `bronze/spotify/ingestion_date=YYYY-MM-DD/datos.parquet`
- `silver/spotify/event_date=YYYY-MM-DD/datos.parquet`
- `gold/spotify/metricas_artistas.parquet`

O por CLI:
```bash
az storage fs file list --account-name <cuenta> --file-system <contenedor> --path "bronze/spotify/"
```

Los Parquet deberían pesar: Bronze ~50-500KB, Silver similar, Gold ~5-50KB.

---

## Notas adicionales

- Si necesitas borrar una ejecución mala, ve a Azure Portal y borra la carpeta con la fecha del día
- Para hacer backfill (reprocesar fechas pasadas), todavía no está automatizado - hay que cambiar el timestamp manualmente en transform.py
- La pérdida de datos normal entre Bronze y Silver es <5% (se eliminan duplicados)
