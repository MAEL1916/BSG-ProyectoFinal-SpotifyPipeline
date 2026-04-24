# Reporte Analítico: Gráficas Obtenidas con Azure Synapse

Este documento presenta los resultados visuales extraídos directamente desde nuestra capa **Gold** (almacenada en formato Parquet en Azure Data Lake Gen2). 

Para generar estos gráficos, utilizamos el motor **Serverless SQL Pool** de **Azure Synapse Analytics**, lo que nos permitió consultar los datos estructurados y cruzarlos (JOINs) mediante SQL estándar sin necesidad de provisionar infraestructura dedicada.

---

##  1. Comparativa de la data

En esta fase, construimos un query analítico para enfrentar las métricas de los artistas extraídos del Dataset crudo (CSV) contra las métricas frescas obtenidas consultando la API pública de Deezer.

WITH MetricasSpotify AS (
    SELECT 
        artist_name as Artista,
        CAST(monthly_listeners_millions_mar2026 AS FLOAT) as Popularidad_Spotify
    FROM 
        OPENROWSET(
            BULK 'https://<datalake>.dfs.core.windows.net/golddata/spotify_wrapped_2025_top50_artists.csv',
            FORMAT = 'CSV',
            PARSER_VERSION = '2.0',
            HEADER_ROW = TRUE
        ) AS s
),
MetricasDeezer AS (
    SELECT 
        nombre_artista as Artista,
        CAST(popularidad_promedio AS FLOAT) as Popularidad_Deezer
    FROM 
        OPENROWSET(
            BULK 'https://<datalake>.dfs.core.windows.net/golddata/metricas_artistas.parquet',
            FORMAT = 'PARQUET'
        ) AS d
)
SELECT TOP 15
    S.Artista,
    S.Popularidad_Spotify AS [Score Spotify (Oyentes/Mes)],
    D.Popularidad_Deezer AS [Score Deezer (Ranking API)]
FROM 
    MetricasSpotify S
INNER JOIN 
    MetricasDeezer D ON S.Artista = D.Artista
ORDER BY 
    S.Popularidad_Spotify DESC;
```

###  Resultados Visuales Generados

A continuación, se muestran las diferentes perspectivas de los datos consultados directamente en el Dashboard de exploración rápida de **Synapse Studio**:

*(Imágenes extraídas de la ejecución en Azure Synapse)*

![Comparativa 1](../Synapse%20Imagenes/SQL%20script%201.png)

![Comparativa 2](../Synapse%20Imagenes/SQL%20script%201-2.png)

![Comparativa 3](../Synapse%20Imagenes/SQL%20script%201-3.png)

![Comparativa 4](../Synapse%20Imagenes/SQL%20script%201-4.png)

---

# 2. Análisis del Top 50 y Tendencias

Adicional al cruce de plataformas, consultamos la capa general consolidada para visualizar relaciones como la popularidad versus la cantidad de canciones analizadas o el recuento general de géneros.

![Comparativa 5](../Synapse%20Imagenes/SQL%20script%201-5.png)

![Comparativa 6](../Synapse%20Imagenes/SQL%20script%201-6.png)

![Comparativa 7](../Synapse%20Imagenes/SQL%20script%201-7.png)

![Comparativa 8](../Synapse%20Imagenes/SQL%20script%201-8.png)

![Comparativa 9](../Synapse%20Imagenes/SQL%20script%201-9.png)

![Comparativa 10](../Synapse%20Imagenes/SQL%20script%201-10.png)

---

##  Conclusión Analítica

A través de **Azure Synapse**, confirmamos que la arquitectura Medallion diseñada cumple su propósito:
* Los datos en la **Capa Gold** están pre-calculados (agregaciones funcionales).
* El cruce entre el CSV histórico y la API dinámica enriquece el modelo.
* La tecnología Serverless SQL de Azure permite extraer valor de negocio de forma inmediata y bajo demanda pagando solo por procesamiento de queries.
