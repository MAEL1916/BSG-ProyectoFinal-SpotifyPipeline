import logging
from datetime import datetime
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
import os
from dotenv import load_dotenv

load_dotenv()

def verificar_ingesta():
    """Verifica que los datos se hayan cargado correctamente en ADLS"""
    try:
        account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
        container_name = 'medallion'
        
        service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=account_key
        )
        
        file_system_client = service_client.get_file_system_client(container_name)
        
        # Verificar Bronze
        bronze_path = f"bronze/spotify/ingestion_date={datetime.now().strftime('%Y-%m-%d')}/datos.parquet"
        bronze_client = file_system_client.get_file_client(bronze_path)
        bronze_props = bronze_client.get_file_properties()
        
        # Verificar Silver
        silver_path = f"silver/spotify/event_date={datetime.now().strftime('%Y-%m-%d')}/datos.parquet"
        silver_client = file_system_client.get_file_client(silver_path)
        silver_props = silver_client.get_file_properties()
        
        # Verificar Gold
        gold_path = "gold/spotify/metricas_artistas.parquet"
        gold_client = file_system_client.get_file_client(gold_path)
        gold_props = gold_client.get_file_properties()
        
        # Crear reporte
        reporte = {
            'timestamp_verificacion': datetime.now(),
            'bronze': {
                'path': bronze_path,
                'size_bytes': bronze_props.size,
                'last_modified': bronze_props.last_modified
            },
            'silver': {
                'path': silver_path,
                'size_bytes': silver_props.size,
                'last_modified': silver_props.last_modified
            },
            'gold': {
                'path': gold_path,
                'size_bytes': gold_props.size,
                'last_modified': gold_props.last_modified
            }
        }
        
        logging.info("=== REPORTE DE INGESTA ===")
        logging.info(f" BRONZE: {bronze_props.size} bytes - {bronze_path}")
        logging.info(f" SILVER: {silver_props.size} bytes - {silver_path}")
        logging.info(f" GOLD: {gold_props.size} bytes - {gold_path}")
        
        return reporte
        
    except Exception as e:
        logging.error(f"Error verificando ingesta: {str(e)}")
        return None