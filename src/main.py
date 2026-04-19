import logging
from pipeline.extract import dwspotify, llamar_api
from pipeline.transform import crear_bronze, limpiar_datos, agregar_metricas
from pipeline.load import guardar_bronze, guardar_silver, guardar_gold
from utils.validador import validar_datos

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Iniciando APi Spotify")
    
    logging.info("--- PASO 1: EXTRACCIÓN ---")
    
    df_spotify = dwspotify()
    if df_spotify is None:
        logging.error("Error al descargar CSV")
        return False
    
    spotify_api = llamar_api()
    if spotify_api is None:
        logging.warning(' API no disponible')
        logging.info(' Continuando solo con CSV')
        spotify_api = None
    
    logging.info("--- PASO 2: TRANSFORMACIÓN BRONZE ---")
    datos_bronze = crear_bronze(df_spotify, spotify_api)
    if datos_bronze is None:
        logging.error("Error al crear Bronze")
        return False
    
    if not validar_datos(datos_bronze, 'bronze'):
        logging.error("Validación Bronze falló")
        return False
    
    logging.info("--- PASO 3: TRANSFORMACIÓN SILVER ---")
    datos_silver = limpiar_datos(datos_bronze)
    if datos_silver is None:
        logging.error('Error al crear Silver')
        return False
    
    if not validar_datos(datos_silver, "silver"):
        logging.error("Validación Silver falló")
        return False
    
    logging.info("--- PASO 4: TRANSFORMACIÓN GOLD ---")
    datos_gold = agregar_metricas(datos_silver)
    if datos_gold is None:
        logging.error("Error al crear Gold")
        return False
    
    if not validar_datos(datos_gold, 'gold'):
        logging.error('Validación Gold falló')
        return False
    
    logging.info("--- PASO 5: CARGA A AZURE ---")
    
    if not guardar_bronze(datos_bronze):
        logging.error("Error al guardar Bronze")
        return False

    if not guardar_silver(datos_silver):
        logging.error("Error al guardar Silver")
        return False
    
    if not guardar_gold(datos_gold):
        logging.error("Error al guardar Gold")
        return False
    
    logging.info("=== PIPELINE COMPLETADO EXITOSAMENTE ===")
    
    # Resumen de registros procesados
    logging.info(f"Bronze: {len(datos_bronze)} registros")
    logging.info(f"Silver: {len(datos_silver)} registros")
    logging.info(f"Gold: {len(datos_gold)} artistas")
    
    return True


if __name__ == "__main__":
    resultado = main()
    if not resultado:
        logging.error("Pipeline falló")
        exit(1)
    else:
        logging.info("Pipeline ejecutado correctamente")
        exit(0)