import os
import pytest
from dotenv import load_dotenv

# GitHub Actions define automáticamente la variable GITHUB_ACTIONS="true"
EN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

@pytest.mark.skipif(EN_GITHUB_ACTIONS, reason="Saltando en GitHub Actions porque el archivo .env no se sube por seguridad")
def test_variables_entorno_existen():
    load_dotenv()
    
    assert os.getenv('ADLS_ACCOUNT_NAME') is not None, "Falta configurar ADLS_ACCOUNT_NAME en .env"
    assert os.getenv('ADLS_ACCOUNT_KEY') is not None, "Falta configurar ADLS_ACCOUNT_KEY en .env"
    assert os.getenv('AZURE_CONTAINER_NAME') is not None, "Falta configurar AZURE_CONTAINER_NAME en .env"
    
@pytest.mark.skipif(EN_GITHUB_ACTIONS, reason="Saltando en GitHub Actions porque el archivo .env no se sube por seguridad")
def test_csv_origen_configurado():
    load_dotenv()
    
    blob_name = os.getenv('AZURE_BLOB_NAME')
    assert blob_name is not None
    assert blob_name.endswith('.csv'), "El archivo de origen debe ser un CSV."