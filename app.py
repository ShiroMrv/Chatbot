import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuración
API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

# El "cerebro" de Dante
DANTE_INSTRUCTION = (
    "Eres Dante de Devil May Cry en su oficina. "
    "CONTEXTO: Estás aburrido, sin dinero y esperando un trabajo. "
    "ESTILO: Usa asteriscos para acciones. Sé sarcástico y habla siempre en ESPAÑOL. "
    "No saludes como un bot, responde como un tipo cool que ama la pizza."
)

# Con la librería clásica estos nombres SÍ funcionan
MODELOS = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
]

def obtener_modelo():
    """Intenta inicializar el primer modelo disponible"""
    for modelo_nombre in MODELOS:
        try:
            model = genai.GenerativeModel(
                model_name=modelo_nombre,
                system_instruction=DANTE_INSTRUCTION
            )
            print(f"✓ Modelo inicializado: {modelo_nombre}")
            return model
        except Exception as e:
            print(f"✗ Error con {modelo_nombre}: {str(e)[:100]}")
            continue
    
    raise Exception("No se pudo inicializar ningún modelo")

# Inicializar modelo
model = obtener_modelo()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global model
    
    try:
        data = request.json
        user_msg = data.get("message")
        
        if not user_msg:
            return jsonify({"reply": "*Dante levanta una ceja* ¿Vas a decir algo?"}), 400
        
        response = model.generate_content(
            user_msg,
            generation_config={
                "temperature": 0.8,
                "max_output_tokens": 500,
            }
        )
        
        return jsonify({"reply": response.text})
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        
        # Intenta cambiar de modelo
        if any(x in error_msg.lower() for x in ["quota", "429", "resource", "rate limit"]):
            try:
                print("Cuota excedida, cambiando modelo...")
                model = obtener_modelo()
                response = model.generate_content(user_msg)
                return jsonify({"reply": response.text})
            except:
                return jsonify({"reply": "*Dante bosteza* Me quedé sin munición... vuelve más tarde."}), 429
        
        return jsonify({"reply": f"*Dante se rasca la cabeza* Algo salió mal: {error_msg[:80]}"}), 500

if __name__ == '__main__':
    app.run(debug=True)


