# Proyecto Final: Pipeline Multi-Cloud Spotify Analytics

**Autor:** Elias Martinez  
**Curso:** Proyectos reales de Ingeniería de Datos con Python  
**Institución:** BSG Institute  
**Fecha:** Abril 2026

---

##  Descripción

Pipeline ETL que integra datos de Spotify desde múltiples fuentes (CSV en Azure Blob Storage y API de Spotify en tiempo real) y los procesa siguiendo arquitectura Medallion (Bronze → Silver → Gold) almacenando los resultados en Azure Synapse Analytics.

---

##  Arquitectura

TODO: Agregar diagrama

---

##  Instalación

Ver [docs/SETUP.md](docs/SETUP.md)

---

##  Estructura de Datos

- **Bronze:** Datos crudos sin procesar
- **Silver:** Datos limpios y validados
- **Gold:** Datos agregados listos para análisis

---

##  Decisiones Técnicas

1. Azure como proveedor principal por compatibilidad con entorno laboral
2. Spotipy para facilitar integración con API de Spotify
3. Arquitectura modular para separación de responsabilidades

---

##  Costos Estimados

TODO: Documentar costos

---

##  Seguridad

Credenciales manejadas con variables de ambiente (`.env`)
