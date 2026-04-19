import pandas
import logging
from io import BytesIO
import requests
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

def dwspotify():
    try:
        from utils.conexion import conectar_azure_blob  # ← SIN 'src.'
        
        blob_service = conectar_azure_blob()
        
        if not blob_service:
            logging.error("Error en dwspotify: No se pudo conectar a Azure")
            return None
        
        contenedor = os.getenv('AZURE_CONTAINER_NAME')
        blob_name = os.getenv("AZURE_BLOB_NAME")
        
        logging.info(f"Descargando {blob_name} desde {contenedor}")
        
        blob_client = blob_service.get_blob_client(container=contenedor, blob=blob_name)
        datos = blob_client.download_blob().readall()
        
        df_spotify = pandas.read_csv(BytesIO(datos))
        
        logging.info(f'Archivo descargado: {len(df_spotify)} registros')
        return df_spotify
        
    except Exception as e:
        logging.error(f"Error en dwspotify: {str(e)}")
        return None


def llamar_api():
    """API DEEZER - NO requiere autenticación"""
    try:
        logging.info("Conectando a Deezer API")
        artistas_data = []
        
        # Top artistas IDs de Deezer (públicos)
        artistas_ids = [
            75491,    # Eminem
            246791,   # Post Malone  
            4050205,  # The Weeknd
            1424954,  # Drake
            12246,    # Daft Punk
            145,      # Rihanna
            110848,   # Ed Sheeran
            892,      # Arctic Monkeys
            4495513,  # Bad Bunny
            12774,    # Ariana Grande
        ]
        
        for artist_id in artistas_ids:
            try:
                # Obtener info del artista
                url = f"https://api.deezer.com/artist/{artist_id}"
                response = requests.get(url, timeout=10)
                
                if response.status_code != 200:
                    logging.warning(f"Error al obtener artista {artist_id}: {response.status_code}")
                    continue
                
                artista = response.json()
                
                # Obtener top tracks
                tracks_url = f"https://api.deezer.com/artist/{artist_id}/top?limit=5"
                tracks_response = requests.get(tracks_url, timeout=10)
                
                if tracks_response.status_code != 200:
                    continue
                
                tracks_data = tracks_response.json()
                
                for track in tracks_data.get('data', [])[:5]:
                    artistas_data.append({
                        'nombre_artista': artista['name'],
                        'id_artista': str(artist_id),
                        'cancion': track['title'],
                        'popularidad': track.get('rank', 0),
                        'followers': artista.get('nb_fan', 0),
                        'generos': 'Music'  # Deezer no expone géneros en API pública
                    })
                
            except Exception as e:
                logging.warning(f"Error procesando artista {artist_id}: {str(e)}")
                continue
        
        if len(artistas_data) == 0:
            logging.error("No se obtuvieron datos de Deezer API")
            return None
        
        df_api = pandas.DataFrame(artistas_data)
        logging.info(f"Datos de Deezer API obtenidos: {len(df_api)} registros")
        return df_api
        
    except Exception as e:
        logging.error(f"Error en llamar_api: {str(e)}")
        return None

# CÓDIGO DE SPOTIFY 
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def llamar_api_spotify():
    try:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        logging.info("Conectado a Spotify API")
        
        artistas_data = []
        top_artistas = ['Bad Bunny', 'Taylor Swift', 'Drake', 'The Weeknd', 'Ed Sheeran', 
                        'Ariana Grande', 'Justin Bieber', 'Billie Eilish', 'Post Malone', 'Dua Lipa']
        
        for nombre in top_artistas:
            try:
                resultados = sp.search(q=nombre, type='artist', limit=1)
                if resultados['artists']['items']:
                    artista = resultados['artists']['items'][0]
                    top_tracks = sp.artist_top_tracks(artista['id'], country='US')
                    
                    for track in top_tracks['tracks'][:5]:
                        artistas_data.append({
                            'nombre_artista': artista['name'],
                            'id_artista': artista['id'],
                            'cancion': track['name'],
                            'popularidad': track['popularity'],
                            'followers': artista['followers']['total'],
                            'generos': ', '.join(artista['genres'][:3]) if artista['genres'] else 'N/A'
                        })
            except Exception as e:
                logging.warning(f"Error buscando {nombre}: {str(e)}")
                continue
        
        spotify_api = pandas.DataFrame(artistas_data)
        logging.info(f"Datos de API obtenidos: {len(spotify_api)} registros")
        return spotify_api
        
    except Exception as e:
        logging.error(f"Error en llamar_api_spotify: {str(e)}")
        return None
"""