# Asistente de Voz con Spotify

Este proyecto es un asistente de voz que interactúa con Spotify, permitiendo controlar la reproducción de música y obtener recomendaciones mediante comandos de voz.

## Características

- Interfaz gráfica de usuario (GUI) para una interacción visual
- Reconocimiento de voz para recibir comandos
- Integración con Spotify para reproducir y recomendar música
- Uso de inteligencia artificial para procesar comandos y generar recomendaciones

## Requisitos

- Python 3.7+
- Cuenta de Spotify Premium
- Credenciales de desarrollador de Spotify
- Clave de API de Google (para el modelo Gemini)

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/Davidcrz14/asistente.git
   cd asistente
   ```

2. Instala las dependencias:
   ```
   pip install spotipy google-generativeai speech_recognition PyQt6 qtawesome
   ```

3. Configura las variables de entorno con tus credenciales de Spotify y Google:
   ```
   export SPOTIPY_CLIENT_ID='tu_client_id'
   export SPOTIPY_CLIENT_SECRET='tu_client_secret'
   export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
   export GOOGLE_API_KEY='tu_clave_api_de_google'
   ```

## Uso

1. Ejecuta la aplicación GUI:
   ```
   python gui_app.py
   ```

2. Haz clic en el botón del micrófono y di tu comando.

3. La aplicación procesará tu comando y ejecutará la acción correspondiente.

## Comandos disponibles

- **Obtener canción actual**: "¿Qué canción está sonando?"
- **Reproducir una canción**: "Reproduce [nombre de la canción] de [artista]"
- **Recomendar música**: "Recomiéndame música como [artista/género]"
- **Inspeccionar playlists**: "Mira mis canciones y dame algo bueno"
- **Recomendar basado en historial**: "Recomiéndame una canción basada en mi historial"

## Estructura del proyecto

- `main.py`: Contiene la lógica principal del asistente
- `commands/spotify_commands.py`: Implementa las funciones de interacción con Spotify
- `gui_app.py`: Implementa la interfaz gráfica de usuario
- `historial_canciones.db`: Base de datos SQLite para almacenar el historial de reproducción

## Notas adicionales

- Asegúrate de tener una conexión a Internet estable para el reconocimiento de voz y la interacción con Spotify.
- La primera vez que ejecutes la aplicación, deberás autorizar el acceso a tu cuenta de Spotify.
- El modelo de IA utilizado (Gemini) requiere una conexión a Internet para funcionar.

## Solución de problemas

Si encuentras problemas con el reconocimiento de voz o la reproducción de música, verifica:

1. Tu conexión a Internet
2. La configuración correcta de las credenciales de Spotify y Google
3. Que tu cuenta de Spotify sea Premium
4. Que tengas un dispositivo activo en Spotify para la reproducción

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de enviar un pull request.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
