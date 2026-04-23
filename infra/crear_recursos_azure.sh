
# La idea era usar Terraform aquí pero no me dió tiempo de aprenderlo bien 
# para este entregable. Así que dejé los comandos de la CLI de Azure
# que usé paso a paso por si se me olvidaba qué cree.

RESOURCE_GROUP="proyecto3-eliasm"
LOCATION="eastus"
STORAGE_ACCOUNT="maelproyecto3"

echo "1. Creando Grupo de Recursos..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "2. Creando Storage Account (Data Lake Gen 2)..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --enable-hierarchical-namespace true

echo "3. Creando los contenedores (medallion y source-data)..."
# Tuve que sacar la key primero:
ACCOUNT_KEY=$(az storage account keys list -g $RESOURCE_GROUP -n $STORAGE_ACCOUNT --query "[0].value" -o tsv)

az storage container create --name "source-data" --account-name $STORAGE_ACCOUNT --account-key $ACCOUNT_KEY
az storage container create --name "medallion" --account-name $STORAGE_ACCOUNT --account-key $ACCOUNT_KEY

echo "¡Listo! El resto (las carpetas bronze, silver, gold) las crea el script de python en load.py"