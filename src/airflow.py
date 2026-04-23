import logging
from datetime import datetime
import pandas as pd
from azure.storage.filedatalake import DataLakeServiceClient
import os
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Silenciamos todos los logs técnicos y aburridos de la conexión con Azure
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

def verificar_ingesta():
    try:
        account_name = os.getenv('ADLS_ACCOUNT_NAME')
        account_key = os.getenv('ADLS_ACCOUNT_KEY')
        
        # Si tienes tus credenciales de otra forma en el .env, asegúrate de que sean las correctas
        if not account_name:
            print("No encontré ADLS_ACCOUNT_NAME. Revisa tu archivo .env.")
            return None

        container_name = 'medallion'
        
        service_client = DataLakeServiceClient(
            account_url=f"https://{account_name}.dfs.core.windows.net",
            credential=account_key
        )
        
        file_system_client = service_client.get_file_system_client(container_name)
        
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        # Rutas
        bronze_path = f"bronze/spotify/ingestion_date={hoy}/datos.parquet"
        silver_path = f"silver/spotify/event_date={hoy}/datos.parquet"
        gold_path = "gold/spotify/metricas_artistas.parquet"
        
        # --- BRONZE ---
        bronze_client = file_system_client.get_file_client(bronze_path)
        bronze_props = bronze_client.get_file_properties()
        print(f"   ↳ Tamaño: {bronze_props.size / 1024:.2f} KB")
        
        # Descargar Bronze con Pandas
        b_data = bronze_client.download_file().readall()
        df_bronze = pd.read_parquet(BytesIO(b_data))
        print(f"   ↳ Registros totales: {len(df_bronze)}")
        print(f"   ↳ Por fuente:\n{df_bronze['fuente'].value_counts().to_string()}")

        # --- SILVER ---
        silver_client = file_system_client.get_file_client(silver_path)
        silver_props = silver_client.get_file_properties()
        print(f"   ↳ Tamaño: {silver_props.size / 1024:.2f} KB")
        
        s_data = silver_client.download_file().readall()
        df_silver = pd.read_parquet(BytesIO(s_data))
        print(f"   ↳ Registros limpios: {len(df_silver)}")

        # --- GOLD ---
        gold_client = file_system_client.get_file_client(gold_path)
        gold_props = gold_client.get_file_properties()
        print(f"   ↳ Tamaño: {gold_props.size / 1024:.2f} KB")
        
        g_data = gold_client.download_file().readall()
        df_gold = pd.read_parquet(BytesIO(g_data))
        print(f"   ↳ Artistas agregados: {len(df_gold)}")

        print("\n muestra informacion cargada")
        muestra = df_gold[['nombre_artista', 'total_canciones', 'popularidad_maxima']].head(5)
        print(muestra.to_markdown())
        
        return True
        
    except Exception as e:
        print(f"\n Error verificando ingesta en Azure: {str(e)}")
        return None

if __name__ == "__main__":
    verificar_ingesta()