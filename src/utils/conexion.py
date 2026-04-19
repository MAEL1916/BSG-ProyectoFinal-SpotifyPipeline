import os
import logging
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

def conectar_azure_blob():

    try:
        conexion = os.getenv('CONEXION_AZURE')
        
        if not conexion:
            logging.error("Error en conectar_azure_blob: No se encontró CONEXION_AZURE en .env")
            return None
            
        blob_service = BlobServiceClient.from_connection_string(conexion)
        logging.info("Conexión exitosa a Azure Blob Storage")
        return blob_service
        
    except Exception as e:
        logging.error(f"Error en conectar_azure_blob: {str(e)}")
        return None

# TODO: 
def conectar_adls():

    try:
        cuenta = os.getenv("ADLS_ACCOUNT_NAME")
        logging.info('Conexión a ADLS iniciada')
        return cuenta
    except Exception as e:
        logging.error(f"Error en conectar_adls: {str(e)}")
        return None