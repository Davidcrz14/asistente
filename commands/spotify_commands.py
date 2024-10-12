import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import google.generativeai as genai
import random

# Configuración de Spotify (mantén esto igual)
SPOTIPY_CLIENT_ID = '3ded45471ca6428ab7544c45ee48d87f'
SPOTIPY_CLIENT_SECRET = 'bd4f9bf524d54a39a60a477068ea8054'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Inicializa la conexión con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-read-currently-playing user-read-playback-state user-modify-playback-state"))

# Configuración de Gemini (asegúrate de que esto esté en sync con main.py)
genai.configure(api_key='AIzaSyD3D35igAJd-q-Eoi_ZFHKnJ8DCeYXdzmw')

model = genai.GenerativeModel(model_name="gemini-1.5-pro")

def cancion_actual():
    current_track = sp.current_user_playing_track()
    if current_track is not None:
        return json.dumps({
            "command": "actualcancion",
            "cancion": current_track['item']['name'],
            "artista": current_track['item']['artists'][0]['name']
        })
    else:
        return json.dumps({"command": "actualcancion", "error": "No se está reproduciendo ninguna canción"})

def reproducir_cancion(cancion, artista, uri=None):
    try:
        if uri:
            sp.start_playback(uris=[uri])
        else:
            results = sp.search(q=f"track:{cancion} artist:{artista}", type="track", limit=1)
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                sp.start_playback(uris=[track_uri])
            else:
                return json.dumps({"command": "cancion", "error": "Canción no encontrada"})

        return json.dumps({
            "command": "cancion",
            "cancion": cancion,
            "artista": artista,
            "mensaje": "Reproduciendo la canción"
        })
    except spotipy.exceptions.SpotifyException as e:
        return json.dumps({"command": "cancion", "error": f"Error al reproducir: {str(e)}"})

def recomendar_musica(gustos, contexto_completo):
    try:
        # Buscar el artista
        artista_principal = gustos.split()[-1]  # Toma la última palabra como el artista principal
        results = sp.search(q=artista_principal, type="artist", limit=1)
        if results['artists']['items']:
            artist = results['artists']['items'][0]
            artist_id = artist['id']

            # Obtener las top tracks del artista
            top_tracks = sp.artist_top_tracks(artist_id)['tracks']

            try:
                # Intentar usar Gemini para seleccionar la canción
                prompt = f"""
                Contexto del usuario: "{contexto_completo}"
                Artista principal: {artist['name']}

                Top canciones del artista:
                {', '.join([track['name'] for track in top_tracks[:10]])}

                Basándote en el contexto emocional del usuario y las canciones disponibles del artista,
                selecciona la canción más apropiada. Responde solo con el nombre de la canción, sin explicaciones adicionales.
                """

                response = model.generate_content(prompt)
                cancion_seleccionada = response.text.strip()
            except Exception as e:
                print(f"Error al usar Gemini: {e}")
                # Si falla Gemini, seleccionar una canción aleatoria
                cancion_seleccionada = random.choice(top_tracks)['name']

            # Buscar la canción seleccionada entre las top tracks
            cancion_recomendada = next((track for track in top_tracks if track['name'].lower() == cancion_seleccionada.lower()), None)

            if not cancion_recomendada:
                # Si no se encuentra la canción exacta, buscar en Spotify
                search_results = sp.search(q=f"track:{cancion_seleccionada} artist:{artist['name']}", type="track", limit=1)
                if search_results['tracks']['items']:
                    cancion_recomendada = search_results['tracks']['items'][0]

            if cancion_recomendada:
                resultado_reproduccion = reproducir_cancion(
                    cancion_recomendada['name'],
                    cancion_recomendada['artists'][0]['name'],
                    cancion_recomendada['uri']
                )
                return {
                    "command": "recomendacion",
                    "gustos": gustos,
                    "contexto": contexto_completo,
                    "artista_original": artist['name'],
                    "cancion_recomendada": {
                        "nombre": cancion_recomendada['name'],
                        "artista": cancion_recomendada['artists'][0]['name'],
                        "album": cancion_recomendada['album']['name'],
                        "uri": cancion_recomendada['uri']
                    },
                    "reproduccion": json.loads(resultado_reproduccion)
                }

        return {"command": "recomendacion", "error": "No se pudo generar una recomendación"}
    except Exception as e:
        print(f"Error en recomendar_musica: {e}")
        return {"command": "recomendacion", "error": f"Error al generar recomendación: {str(e)}"}

def inspeccionar_playlists_y_recomendar():
    try:
        # Obtener las playlists del usuario
        playlists = sp.current_user_playlists()
        todas_las_canciones = []

        # Recopilar canciones de las primeras 5 playlists (o menos si el usuario tiene menos)
        for playlist in playlists['items'][:5]:
            results = sp.playlist_tracks(playlist['id'])
            canciones_playlist = [item['track'] for item in results['items'] if item['track']]
            todas_las_canciones.extend(canciones_playlist[:10])  # Tomar las primeras 10 canciones de cada playlist

        if not todas_las_canciones:
            return {"command": "inspector", "error": "No se encontraron canciones en tus playlists"}

        # Seleccionar una canción aleatoria de las recopiladas
        cancion_recomendada = random.choice(todas_las_canciones)

        # Generar un resumen de las playlists inspeccionadas
        resumen_playlists = ", ".join([playlist['name'] for playlist in playlists['items'][:5]])

        # Intentar reproducir la canción recomendada
        resultado_reproduccion = reproducir_cancion(
            cancion_recomendada['name'],
            cancion_recomendada['artists'][0]['name'],
            cancion_recomendada['uri']
        )

        return {
            "command": "inspector",
            "playlists_inspeccionadas": resumen_playlists,
            "cancion_recomendada": {
                "nombre": cancion_recomendada['name'],
                "artista": cancion_recomendada['artists'][0]['name'],
                "album": cancion_recomendada['album']['name'],
                "uri": cancion_recomendada['uri']
            },
            "reproduccion": json.loads(resultado_reproduccion)
        }
    except Exception as e:
        print(f"Error en inspeccionar_playlists_y_recomendar: {e}")
        return {"command": "inspector", "error": f"Error al inspeccionar playlists: {str(e)}"}
