import pandas
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def crear_bronze(df_spotify, spotify_api):
    try:
        df_spotify['fuente'] = 'CSV'
        
        spotify_api["fuente"] = "API"
        
        # TODO: mejorar esto
        # Combinar ambos DataFrames
        datos_completos = pandas.concat([df_spotify, spotify_api], ignore_index=True)
        
        datos_completos['ingestion_timestamp'] = datetime.now()
        
        logging.info(f"Capa Bronze creada: {len(datos_completos)} registros")
        return datos_completos
        
    except Exception as e:
        logging.error(f"Error en crear_bronze: {str(e)}")
        return None


def limpiar_datos(datos_completos):
    try:
        datos_silver = datos_completos.copy()
        
        datos_silver = datos_silver.dropna(subset=['nombre_artista'])
        
        datos_silver = datos_silver.drop_duplicates(
            subset=['id_artista', 'cancion'],
            keep='first'
        )
        
        datos_silver['fecha_procesamiento'] = datetime.now()
        
        logging.info(f'Capa Silver creada: {len(datos_silver)} registros')
        return datos_silver
        
    except Exception as e:
        logging.error(f"Error en limpiar_datos: {str(e)}")
        return None


def agregar_metricas(datos_silver):
    try:
        datos_gold = datos_silver.groupby(['nombre_artista', 'id_artista']).agg({
            'cancion': 'count',
            'popularidad': ['mean', 'max'],
            'fuente': 'first'
        }).reset_index()
        
        datos_gold.columns = [
            'nombre_artista',
            'id_artista', 
            'total_canciones',
            'popularidad_promedio',
            'popularidad_maxima',
            'fuente_datos'
        ]
        
        datos_gold['popularidad_promedio'] = datos_gold['popularidad_promedio'].round(2)
        
        logging.info(f"Capa Gold creada: {len(datos_gold)} artistas únicos")
        return datos_gold
        
    except Exception as e:
        logging.error(f"Error en agregar_metricas: {str(e)}")
        return None