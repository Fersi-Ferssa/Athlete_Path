import google.generativeai as genai

# Configura la clave de la API de Google Gemini
genai.configure(api_key="AIzaSyCDy1JgkjlY-RXN_CJgM1fTfOVKTsuvh9I")

def analyze_video(video_url):
    # Crear la configuración de generación
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    # Inicializa el modelo de generación
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-002",
        generation_config=generation_config,
    )

    # Iniciar la sesión de chat
    chat = model.start_chat()

    # Enviar el mensaje con el video para analizarlo
    response = chat.send_message({
        "role": "user",
        "parts": [
            "Necesito que hagas el rol de un juez/analista olímpico. Te voy a mandar un video y quisiera que me evalues lo siguiente: "
            "Disciplina, errores o mejoras que consideras que debería tener la técnica y si pudieras darle un puntaje cuál sería. "
            f"Aquí va el video: {video_url}"
        ]
    })

    # Retornar el análisis como texto
    return response.text