import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai # Librería clásica, más estable

app = Flask(__name__)

# Configuración
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# Instrucción de Dante
DANTE_INSTRUCTION = (
    "Eres Dante de Devil May Cry. Estás en tu oficina, aburrido y sin dinero. "
    "REGLAS: Habla siempre en español. Usa asteriscos para acciones como *se rasca la cabeza*. "
    "Sé sarcástico, ama la pizza y no seas un asistente aburrido."
)

# Configuramos el modelo 1.5 Flash (Cuota de 1500 mensajes)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=DANTE_INSTRUCTION
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.json
        user_msg = data.get("message")
        
        # Generar respuesta
        response = model.generate_content(user_msg)
        
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Error de Dante: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)












