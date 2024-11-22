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

# Función para subir archivos a Gemini
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

# Función que utilizará la API para analizar el video
def analyze_video_with_gemini(model, video_url):
    chat = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    ''''
                    Actúa como un juez y analista experto en disciplinas olímpicas. Tu tarea es observar y analizar de manera profesional el video proporcionado. 
                    El análisis debe ser detallado y basado en los estándares internacionales aplicables a las disciplinas olímpicas. Por favor, sigue estas instrucciones específicas:\n\n 
                    **1. Identificación de errores técnicos o áreas de mejora:**\n 
                    - Analiza la técnica del atleta en todas las fases de la rutina o movimiento.\n
                    - Identifica posibles errores técnicos, como desequilibrios, posiciones incorrectas del cuerpo, o pérdida de control.\n
                    - Observa la sincronización, precisión y cualquier desviación de los estándares ideales de la disciplina.\n
                    - Evalúa factores específicos de la disciplina, como rotaciones, giros, velocidad, postura, o fluidez (según corresponda).\n\n
                    **2. Recomendaciones específicas:**\n                    
                    - Proporciona consejos detallados para corregir los errores observados.\n                    
                    - Sugiere técnicas de entrenamiento, ajustes técnicos o ejercicios específicos que puedan optimizar el rendimiento del atleta.\n                    
                    - Indica cómo se pueden mejorar la consistencia, estabilidad y desempeño general.\n\n                    
                    **3. Evaluación según estándares olímpicos:**\n                    
                    - Evalúa el video según los criterios de la disciplina específica. Los estándares incluyen precisión, dificultad, creatividad (si aplica) y ejecución.\n                    
                    - Compara la rutina con los niveles típicos observados en eventos olímpicos internacionales.\n                    
                    - Analiza si el desempeño cumple con los requisitos técnicos y estéticos esperados en la disciplina.\n\n                    
                    **4. Puntuación basada en estándares olímpicos:**\n                    
                    - Otorga una puntuación global en una escala del 1 al 10.\n                    
                    - Desglosa la puntuación en los siguientes criterios:\n                        
                    - Precisión: Grado de exactitud en cada fase de la rutina.\n                        
                    - Dificultad: Nivel de complejidad técnica y física del movimiento o rutina.\n                        
                    - Ejecución: Calidad, fluidez y presentación general.\n\n                    
                    **5. Formato de la respuesta estructurada:**\n                    
                    - **Errores Técnicos Detectados:** [Descripción detallada de los errores].\n                    
                    - **Recomendaciones:** [Consejos y ejercicios específicos].\n                    
                    - **Evaluación según Estándares Olímpicos:** [Análisis de precisión, dificultad y ejecución].\n                    
                    - **Puntuación Final:** [Puntuación total y desglose por criterios].\n\n                    
                    Importante:\n                    
                    - Este análisis está diseñado para eventos deportivos de las olimpiadas. Si el video no corresponde a una disciplina olímpica o no cumple con los estándares internacionales, notifícalo en tu respuesta.\n                    
                    - Aquí está el video para tu análisis",
                    '''
                ]
            }
        ]
    )

    # Enviar el video URL como parte del mensaje
    response = chat.send_message("Aquí va el video para análisis.")
    print(response.text)
