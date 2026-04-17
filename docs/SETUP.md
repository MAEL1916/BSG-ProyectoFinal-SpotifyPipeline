# Guía de Instalación y Configuración

**Proyecto:** Pipeline Spotify Analytics  
**Autor:** Elias Martinez  
**Fecha:** Abril 2026

---

# Guía de Instalación

## Requisitos Previos

### 1. Azure CLI

#### macOS:
```bash
brew install azure-cli
az --version

----

##  Prerrequisitos

-  Python 3.9+ (ya instalado con conda)
-  Azure CLI (ya configurado del Proyecto 3)
-  Cuenta de Azure con credenciales activas
-  Git instalado
-  Cuenta de Spotify Developer

---

## Reutilizando Configuración 

Este proyecto reutiliza parte de la infraestructura del **Proyecto 3**:
- Azure Blob Storage (mismo storage account)
- Credenciales de Azure ya configuradas
- Azure CLI ya autenticado

---

## Nueva Configuración

### **1. Spotify Developer Account**

1. Ir a: https://developer.spotify.com/dashboard
2. Crear App:
   - **App name:** Nombre de tu proyecto
   - **App description:** Pipeline ETL para análisis
   - **Redirect URI:** http://localhost:8888/callback
3. Copiar credenciales (Client ID y Secret)

### **2. Azure Synapse Analytics** 

```bash
# Verificar servicios disponibles en tu suscripción
az account show

# Listar resource groups existentes
az group list --output table

# TODO: Crear Synapse workspace en proceso