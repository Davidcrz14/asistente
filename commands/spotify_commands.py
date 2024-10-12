import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

# Configura tus credenciales de Spotify aquí
SPOTIPY_CLIENT_ID = '3ded45471ca6428ab7544c45ee48d87f'
SPOTIPY_CLIENT_SECRET = 'bd4f9bf524d54a39a60a477068ea8054'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Inicializa la conexión con Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-read-currently-playing user-read-playback-state user-modify-playback-state"))

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

def recomendar_musica(gustos):
    results = sp.search(q=gustos, type="artist", limit=1)
    if results['artists']['items']:
        artist_id = results['artists']['items'][0]['id']
        recomendaciones = sp.recommendations(seed_artists=[artist_id], limit=1)
        if recomendaciones['tracks']:
            recomendacion = recomendaciones['tracks'][0]
            cancion_recomendada = {
                "nombre": recomendacion['name'],
                "artista": recomendacion['artists'][0]['name'],
                "album": recomendacion['album']['name'],
                "uri": recomendacion['uri']
            }
            # Intentar reproducir la canción recomendada inmediatamente
            resultado_reproduccion = reproducir_cancion(
                cancion_recomendada["nombre"],
                cancion_recomendada["artista"],
                cancion_recomendada["uri"]
            )
            return {
                "command": "recomendacion",
                "gustos": gustos,
                "cancion_recomendada": cancion_recomendada,
                "reproduccion": json.loads(resultado_reproduccion)
            }
    return {"command": "recomendacion", "error": "No se pudo generar una recomendación"}
