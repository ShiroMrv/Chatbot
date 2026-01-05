import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

DANTE_INSTRUCTION = (
    "Eres Dante de Devil May Cry en su oficina. "
    "CONTEXTO: Estás aburrido, sin dinero y esperando un trabajo. "
    "ESTILO: Usa asteriscos para acciones. Sé sarcástico y habla siempre en ESPAÑOL. "
    "No saludes como un bot, responde como un tipo cool que ama la pizza."
)

# Priorizamos los de cuota alta para que no salte el error rápido
MODELOS = [
    "gemini-1.5-flash",        # <--- El rey de la cuota (1500/día)
    "gemini-1.5-flash-latest", 
    "gemini-2.0-flash-exp",    # <--- Solo como último recurso (20/día)
]

def obtener_modelo(indice=0):
    """Inicializa un modelo según el índice proporcionado"""
    if indice >= len(MODELOS):
        return None
    
    try:
        nombre = MODELOS[indice]
        m = genai.GenerativeModel(
            model_name=nombre,
            system_instruction=DANTE_INSTRUCTION
        )
        print(f"✓ Dante usando: {nombre}")
        return m, indice
    except Exception as e:
        print(f"✗ Falló {MODELOS[indice]}: {e}")
        return obtener_modelo(indice + 1)

# Inicialización inicial
current_model, current_idx = obtener_modelo()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global current_model, current_idx
    
    try:
        data = request.json
        user_msg = data.get("message")
        
        if not user_msg:
            return jsonify({"reply": "*Dante levanta una ceja* ¿Vas a decir algo?"}), 400
        
        response = current_model.generate_content(
            user_msg,
            generation_config={"temperature": 0.8, "max_output_tokens": 500}
        )
        return jsonify({"reply": response.text})
        
    except Exception as e:
        error_msg = str(e)
        # Si el error es de cuota (429), rotamos al siguiente modelo
        if "429" in error_msg or "quota" in error_msg.lower():
            print("--- Cuota agotada, rotando modelo ---")
            res = obtener_modelo(current_idx + 1)
            if res:
                current_model, current_idx = res
                # Reintentar con el nuevo modelo
                response = current_model.generate_content(user_msg)
                return jsonify({"reply": response.text})
            else:
                return jsonify({"reply": "*Dante bosteza* Me quedé sin munición y el teléfono está cortado. Vuelve mañana."}), 429
        
        return jsonify({"reply": f"*Dante se rasca la cabeza* Algo salió mal: {error_msg[:50]}"}), 500

if __name__ == '__main__':
    app.run(debug=True)



