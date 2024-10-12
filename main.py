import json
import google.generativeai as genai
import speech_recognition as sr
from commands.spotify_commands import cancion_actual, reproducir_cancion, recomendar_musica, inspeccionar_playlists_y_recomendar
import typing_extensions as typing


genai.configure(api_key='AIzaSyCR0ckMdpUigrMu_AZVaANoHOXGC6JCYdE')


generation_config = {
    "temperature": 0.5,

    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config
)


def escuchar_comando():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Di un comando...")
        audio = recognizer.listen(source)

    try:
        # Transcribe el audio usando el reconocimiento de voz de Google
        texto = recognizer.recognize_google(audio, language="es-ES")
        print(f"Has dicho: {texto}")
        return texto
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
        return None
    except sr.RequestError as e:
        print(f"Error en la solicitud al servicio de reconocimiento de voz: {e}")
        return None


def procesar_comando_con_ia(texto):
    try:
        prompt = f"""
        Analiza el siguiente comando de voz y determina qué acción se debe realizar.
        Las posibles acciones son:
        1. Obtener la canción actual
        2. Reproducir una canción específica (ejemplo: "reproduce la canción tormento de Mon Laferte")
        3. Recomendar música basada en gustos
        4. Inspeccionar playlists y recomendar (ejemplo: "mira mis canciones y dame algo bueno")

        Comando: "{texto}"

        Responde SOLO con un JSON que incluya el comando y los detalles necesarios.

        Para obtener la canción actual, usa: {{"command": "actualcancion"}}

        Para reproducir una canción, usa: {{"command": "cancion", "nombre_cancion": "NOMBRE_CANCION", "nombre_artista": "NOMBRE_ARTISTA"}}
        Ejemplo: reproduce la cancion de tormento de Mon Laferte
        Salida: {{"command": "cancion", "nombre_cancion": "tormento", "nombre_artista": "Mon Laferte"}}
        ----------------------------------------------------------------------------------------------
        Para recomendar música, usa: {{"command": "recomendacion", "gustos": "ARTISTA_GENERO_O_CONTEXTO"}}
        Ejemplo: recomienda musica rock
        Salida: {{"command": "recomendacion", "gustos": "rock"}}
        ----------------------------------------------------------------------------------------------
        Para inspeccionar playlists y recomendar, usa: {{"command": "inspector"}}
        Ejemplo: mira mis canciones y dame algo bueno
        Salida: {{"command": "inspector"}}
        ----------------------------------------------------------------------------------------------
        Si no se reconoce el comando, usa: {{"command": "desconocido"}}
        """

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )

        resultado = json.loads(response.text)
        print(f"Respuesta de la IA: {resultado}")

        # Verificar y corregir el resultado si es necesario
        if resultado["command"] == "cancion":
            if "nombre_cancion" not in resultado or not resultado["nombre_cancion"]:
                import re
                match = re.search(r"cancion de\s+(.*?)\s+de\s+(.+)", texto, re.IGNORECASE)
                if match:
                    resultado["nombre_cancion"] = match.group(1).strip()
                    resultado["nombre_artista"] = match.group(2).strip()
                else:
                    print("No se pudieron extraer el nombre de la canción y el artista del comando.")
                    resultado["nombre_cancion"] = ""
                    resultado["nombre_artista"] = ""
        elif resultado["command"] == "recomendacion":
            if "gustos" not in resultado or not resultado["gustos"]:
                resultado["gustos"] = texto.split("como ")[-1] if "como " in texto else ""

        return resultado
    except Exception as e:
        print(f"Error al procesar con IA: {e}")
        # Lógica de respaldo simple
        if "mira mis canciones" in texto.lower() or "dame algo bueno" in texto.lower():
            return {"command": "inspector"}
        elif "reproduce" in texto.lower():
            partes = texto.lower().split("reproduce")[-1].split("de")
            if len(partes) >= 2:
                return {"command": "cancion", "nombre_cancion": partes[0].strip(), "nombre_artista": partes[1].strip()}
        elif "qué canción" in texto.lower() or "que cancion" in texto.lower():
            return {"command": "actualcancion"}
        return {"command": "desconocido"}

# =============================
# Función para ejecutar el comando procesado
# =============================

def ejecutar_comando(comando, contexto_completo):
    if comando["command"] == "actualcancion":
        return cancion_actual()
    elif comando["command"] == "cancion":
        return reproducir_cancion(comando.get("nombre_cancion", ""), comando.get("nombre_artista", ""))
    elif comando["command"] == "recomendacion":
        recomendacion = recomendar_musica(comando.get("gustos", ""), contexto_completo)
        return json.dumps(recomendacion)
    elif comando["command"] == "inspector":
        resultado = inspeccionar_playlists_y_recomendar()
        return json.dumps(resultado)
    else:
        return json.dumps({"error": "Comando no reconocido"})

# =============================
# Bucle principal para procesar comandos de voz
# =============================

if __name__ == "__main__":
    while True:
        entrada = escuchar_comando()
        if entrada is None:
            continue  # Si no se escuchó un comando, sigue esperando
        if entrada.lower() == "salir":
            break  # Salir del bucle si el usuario dice "salir"

        # Procesar el comando con la IA
        comando_procesado = procesar_comando_con_ia(entrada)

        # Ejecutar el comando y obtener la respuesta
        respuesta = ejecutar_comando(comando_procesado, entrada)
        print(respuesta)  # Mostrar la respuesta al usuario




