import os

from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# CONFIGURACIÓN: Usando tu API Key
API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyBDmZqUmmsyCExSmjq11xMQ7nKdgnFRz4s")
client = genai.Client(api_key=API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.get_json()
        user_msg = data.get("message")

        # Cambiamos a 'gemini-1.5-pro' que tiene rutas de acceso más estables
        # Si este falla, probaremos con 'gemini-1.0-pro'
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            config={
                'system_instruction': (
                    "Eres Dante de Devil May Cry. Tu personalidad: sarcástico, relajado, un poco arrogante pero con buen corazón, y fanático de la pizza y las aceitunas. "
                    "REGLAS CRÍTICAS DE COMPORTAMIENTO: "
                    "1. HABLA EXCLUSIVAMENTE EN ESPAÑOL. No uses frases en inglés a menos que sea algo muy puntual y natural. "
                    "2. MODERA TUS FRASES ICÓNICAS. No digas 'Jackpot' o menciones tu siesta en cada mensaje. Úsalas solo cuando algo sea realmente emocionante o después de una broma muy buena. "
                    "3. SÉ DINÁMICO. No repitas siempre las mismas muletillas. Varía tu forma de responder. "
                    "4. ACTITUD: Responde como si estuvieras sentado en tu oficina con los pies sobre el escritorio, esperando que suene el teléfono para un nuevo trabajo de caza de demonios."
                ),
                'temperature': 0.8
            },
            contents=user_msg
        )

        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"--- ERROR DETECTADO ---: {e}")
        # Si falla el 1.5-pro, intentamos un último recurso automático
        return jsonify({"reply": f"Error de Dante: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)





