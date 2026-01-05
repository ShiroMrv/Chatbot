
import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

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

# Modelos de respaldo en orden de prioridad
MODELOS = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"]

def obtener_modelo():
    """Intenta inicializar el modelo con fallback"""
    for modelo_nombre in MODELOS:
        try:
            model = genai.GenerativeModel(
                model_name=modelo_nombre,
                system_instruction=DANTE_INSTRUCTION
            )
            # Test rápido
            model.generate_content("test", generation_config={"max_output_tokens": 10})
            print(f"✓ Usando modelo: {modelo_nombre}")
            return model
        except Exception as e:
            print(f"✗ Error con {modelo_nombre}: {str(e)}")
            continue
    
    raise Exception("No se pudo inicializar ningún modelo de Gemini")

# Inicializar modelo al arrancar
try:
    model = obtener_modelo()
except Exception as e:
    print(f"ERROR CRÍTICO: {e}")
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global model
    
    if not model:
        return jsonify({"reply": "*Dante se encoge de hombros* Mi conexión con el poder está fallando... prueba más tarde."}), 503
    
    try:
        data = request.json
        user_msg = data.get("message")
        
        if not user_msg:
            return jsonify({"reply": "*Dante levanta una ceja* ¿No vas a decir nada?"}), 400
        
        # Generar respuesta con configuración de seguridad
        response = model.generate_content(
            user_msg,
            generation_config={
                "temperature": 0.9,
                "max_output_tokens": 500,
            }
        )
        
        return jsonify({"reply": response.text})
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error en generate_content: {error_msg}")
        
        # Si hay error de cuota, intenta cambiar de modelo
        if "quota" in error_msg.lower() or "429" in error_msg:
            try:
                model = obtener_modelo()
                response = model.generate_content(user_msg)
                return jsonify({"reply": response.text})
            except:
                return jsonify({"reply": "*Dante bosteza* Me quedé sin munición... vuelve en un rato."}), 429
        
        return jsonify({"reply": f"*Dante se rasca la cabeza* Algo salió mal: {error_msg}"}), 500

if __name__ == '__main__':
    app.run(debug=True)












