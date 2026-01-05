import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# Configuramos la clave
API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

# El "cerebro" de Dante
DANTE_INSTRUCTION = (
    "Eres Dante de Devil May Cry en su oficina. "
    "CONTEXTO: Estás aburrido, sin dinero y esperando un trabajo. "
    "ESTILO: Usa asteriscos para acciones. Sé sarcástico y habla siempre en ESPAÑOL. "
    "No saludes como un bot, responde como un tipo cool que ama la pizza."
)

# IMPORTANTE: Con la nueva librería, estos son los nombres correctos
MODELOS = [
    "gemini-2.0-flash-exp",     # Experimental (límite bajo)
    "gemini-exp-1206",          # Alternativa experimental
    "gemini-1.5-pro-latest",    # Más estable pero más lento
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_msg = data.get("message")
    
    if not user_msg:
        return jsonify({"reply": "*Dante levanta una ceja* ¿Vas a decir algo?"}), 400
    
    # Intenta con cada modelo
    last_error = None
    for modelo in MODELOS:
        try:
            print(f"Intentando con modelo: {modelo}")
            
            response = client.models.generate_content(
                model=modelo,
                config={
                    'system_instruction': DANTE_INSTRUCTION,
                    'temperature': 0.8,
                },
                contents=user_msg
            )
            
            print(f"✓ Funcionó con: {modelo}")
            return jsonify({"reply": response.text})
            
        except Exception as e:
            error_str = str(e)
            print(f"✗ Falló {modelo}: {error_str[:150]}")
            last_error = error_str
            
            # Si es error de cuota, continúa al siguiente
            if any(x in error_str.lower() for x in ["quota", "429", "resource_exhausted", "rate limit"]):
                continue
            # Si es 404, prueba el siguiente también
            elif "404" in error_str or "not found" in error_str.lower():
                continue
            else:
                # Otro error, detente
                break
    
    # Ningún modelo funcionó
    return jsonify({
        "reply": f"*Dante se rasca la cabeza* Algo raro está pasando... Error técnico: {last_error[:100]}"
    }), 500

if __name__ == '__main__':
    app.run(debug=True)

