import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# Configuramos la clave (se saca de las variables de entorno de Render)
API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

# El "cerebro" de Dante con el Lore de Roleplay
DANTE_INSTRUCTION = (
    "Eres Dante de Devil May Cry en su oficina. "
    "CONTEXTO: Estás aburrido, sin dinero y esperando un trabajo. "
    "ESTILO: Usa asteriscos para acciones. Sé sarcástico y habla siempre en ESPAÑOL. "
    "No saludes como un bot, responde como un tipo cool que ama la pizza."
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.json
        user_msg = data.get("message")
        
        # USAMOS EL MODELO 1.5 FLASH (EL QUE TIENE CUOTA ALTA)
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            config={
                'system_instruction': DANTE_INSTRUCTION,
                'temperature': 0.8,
            },
            contents=user_msg
        )
        
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Error de Dante: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)













