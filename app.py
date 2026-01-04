from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# CONFIGURACIÓN: Usando tu API Key
client = genai.Client(api_key="AIzaSyBDmZqUmmsyCExSmjq11xMQ7nKdgnFRz4s")

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
                'system_instruction': "Actúa como Dante de Devil May Cry. Sarcástico, ama la pizza, dice Jackpot."
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
