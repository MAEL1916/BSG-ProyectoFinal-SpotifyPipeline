import pandas
import logging
from datetime import datetime
import os
from azure.storage.filedatalake import DataLakeServiceClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

def conectar_adls():
    try:
        account_name = os.getenv('ADLS_ACCOUNT_NAME')
        account_key = os.getenv("ADLS_ACCOUNT_KEY")
        
        if not account_name or not account_key:
            logging.error("Error en conectar_adls: Faltan credenciales de ADLS")
            return None
        
        service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=account_key
        )
        
        logging.info('Conexión a ADLS exitosa')
        return service_client
        
    except Exception as e:
        logging.error(f"Error en conectar_adls: {str(e)}")
        return None


def guardar_bronze(datos_bronze):
    try:
        service_client = conectar_adls()
        
        if not service_client:
            return False
        
        # TODO: mejorar esto
        container_name = os.getenv('ADLS_CONTAINER_NAME')
        fecha = datetime.now().strftime('%Y-%m-%d')
        ruta = f"bronze/spotify/ingestion_date={fecha}/datos.parquet"
        
        buffer = datos_bronze.to_parquet(index=False)
        
        file_system_client = service_client.get_file_system_client(container_name)
        file_client = file_system_client.get_file_client(ruta)
        file_client.upload_data(buffer, overwrite=True)
        
        logging.info(f"Datos Bronze guardados en {ruta}")
        return True
        
    except Exception as e:
        logging.error(f"Error en guardar_bronze: {str(e)}")
        return False


def guardar_silver(datos_silver):
    try:
        service_client = conectar_adls()
        
        if not service_client:
            return False
        
        container_name = os.getenv("ADLS_CONTAINER_NAME")
        fecha = datetime.now().strftime("%Y-%m-%d")
        ruta = f'silver/spotify/event_date={fecha}/datos.parquet'
        
        buffer = datos_silver.to_parquet(index=False)
        
        file_system_client = service_client.get_file_system_client(container_name)
        file_client = file_system_client.get_file_client(ruta)
        file_client.upload_data(buffer, overwrite=True)
        
        logging.info(f'Datos Silver guardados en {ruta}')
        return True
        
    except Exception as e:
        logging.error(f"Error en guardar_silver: {str(e)}")
        return False


# TODO: mejorar esto - agregar carga a Synapse
def guardar_gold(datos_gold):
    try:
        service_client = conectar_adls()
        
        if not service_client:
            return False
        
        container_name = os.getenv('ADLS_CONTAINER_NAME')
        ruta = 'gold/spotify/metricas_artistas.parquet'
        
        buffer = datos_gold.to_parquet(index=False)

        file_system_client = service_client.get_file_system_client(container_name)
        file_client = file_system_client.get_file_client(ruta)
        file_client.upload_data(buffer, overwrite=True)
        
        logging.info(f"Datos Gold guardados en {ruta}")
        return True
        
    except Exception as e:
        logging.error(f"Error en guardar_gold: {str(e)}")
        return False