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
    
    logging.info("EXTRACCIÓN")
    
    df_spotify = dwspotify()
    if df_spotify is None:
        print("Error al descargar CSV")
        return False
    
    spotify_api = llamar_api()
    if spotify_api is None:
        print(' API no disponible')
        print(' Continuando solo con CSV')
        spotify_api = None
    
    logging.info("TRANSFORMACIÓN BRONZE")
    datos_bronze = crear_bronze(df_spotify, spotify_api)
    if datos_bronze is None:
        print("Error al crear Bronze")
        return False
    
    if not validar_datos(datos_bronze, 'bronze'):
        print("Validación Bronze falló")
        return False
    
    logging.info("TRANSFORMACIÓN SILVER")
    datos_silver = limpiar_datos(datos_bronze)
    if datos_silver is None:
        print('Error al crear Silver')
        return False
    
    if not validar_datos(datos_silver, "silver"):
        print("Validación Silver falló")
        return False
    
    logging.info("TRANSFORMACIÓN GOLD")
    datos_gold = agregar_metricas(datos_silver)
    if datos_gold is None:
        print("Error al crear Gold")
        return False
    
    if not validar_datos(datos_gold, 'gold'):
        print('Validación Gold falló')
        return False
    
    logging.info("CARGA A AZURE")
    
    if not guardar_bronze(datos_bronze):
        print("Error al guardar Bronze")
        return False

    if not guardar_silver(datos_silver):
        print("Error al guardar Silver")
        return False
    
    if not guardar_gold(datos_gold):
        print("Error al guardar Gold")
        return False
    
    print("Proceso completo")
    
    # Resumen de registros procesados
    print(f"Bronze: {len(datos_bronze)} registros")
    print(f"Silver: {len(datos_silver)} registros")
    print(f"Gold: {len(datos_gold)} artistas")
    
    return True


if __name__ == "__main__":
    resultado = main()
    if not resultado:
        print("Pipeline falló")
        exit(1)
    else:
        print("Pipeline ejecutado correctamente")
        exit(0)