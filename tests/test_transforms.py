import pytest
import pandas as pd
import sys
sys.path.insert(0, 'src')

from pipeline.transform import crear_bronze, limpiar_datos, agregar_metricas

def test_crear_bronze():
    # Datos de prueba del CSV (solo nombre)
    df_csv = pd.DataFrame({'nombre_artista': ['Test']})
    
    # Datos de prueba de la API (más completos)
    df_api = pd.DataFrame({
        'nombre_artista': ['API'],
        'id_artista': ['1'],
        'cancion': ['Song'],
        'popularidad': [80],
        'followers': [1000],
        'generos': ['pop']
    })
    
    # Ejecutar la función
    resultado = crear_bronze(df_csv, df_api)
    
    # Verificar que juntó los 2 registros (1 del CSV + 1 del API)
    assert len(resultado) == 2


def test_limpiar_datos():
    # Datos de prueba con problemas:
    # - Fila 1 y 2 son duplicadas (mismo id_artista y cancion)
    # - Fila 3 tiene nombre_artista = None
    datos = pd.DataFrame({
        'nombre_artista': ['A', 'A', None],
        'id_artista': ['1', '1', '2'],
        'cancion': ['S', 'S', 'X'],
        'ingestion_timestamp': [pd.Timestamp.now()] * 3
    })
    
    # Ejecutar la función
    resultado = limpiar_datos(datos)
    
    # Verificar que solo quede 1 registro (eliminó el duplicado y el None)
    assert len(resultado) == 1
