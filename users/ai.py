import google.generativeai as genai
import time

# Configuración del modelo con la clave de la API de Gemini
def model_configai():
    genai.configure(api_key='AIzaSyCDy1JgkjlY-RXN_CJgM1fTfOVKTsuvh9I') 

    # Configuración de la generación
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    # Crear el modelo
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-002", generation_config=generation_config)
    return model

# Función para subir archivos a Gemini (si es necesario usar otros medios además de texto, como imágenes o PDFs)
def upload_to_gemini(path, mime_type=None):
    """Sube el archivo a Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Archivo '{file.display_name}' subido: {file.uri}")
    return file

# Esperar que los archivos subidos estén activos
def wait_for_files_active(files):
    """Espera hasta que los archivos estén procesados y listos."""
    print("Esperando procesamiento de archivos...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"El archivo {file.name} falló en procesarse")
    print("Archivos listos.")

# Función que utilizará la API para analizar el video con un prompt de juez olímpico
def analyze_video_with_gemini(model, video_url):
    chat = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    '''
                    Actúa como un juez y analista experto en clavados olímpicos. Te enviaré un video de una rutina de clavados y necesito que realices un análisis detallado en base a los siguientes criterios:
                    Identifica posibles errores técnicos o áreas de mejora en la ejecución del clavado.
                    Ofrece recomendaciones específicas para optimizar la técnica.
                    Evalúa la rutina en función de los estándares olímpicos, y asigna una puntuación en una escala del 1 al 10 basada en la precisión, dificultad y ejecución.
                    Aquí está el video para tu análisis: " + video_url.
                    '''
                ]
            }
        ]
    )

    # Enviar el video URL como parte del mensaje
    response = chat.send_message("Aquí va el video para análisis.")
    print(response.text)
