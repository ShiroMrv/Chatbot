import os
from flask import Flask, render_template, request, jsonify
from groq import Groq # Cambiamos de Google a Groq

app = Flask(__name__)

# Configurá tu nueva API Key en Render con el nombre GROQ_API_KEY
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DANTE_INSTRUCTION = (
    "Eres Dante de Devil May Cry. Estás en tu oficina, aburrido. "
    "Responde siempre en español, sé sarcástico, usa asteriscos para acciones. "
    "No eres un asistente, eres un cazador de demonios perezoso."
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_msg = request.json.get("message")
        
        # Usamos Llama 3.3, que es una bestia y es gratis en Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": DANTE_INSTRUCTION},
                {"role": "user", "content": user_msg}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
        )
        
        reply = chat_completion.choices[0].message.content
        return jsonify({"reply": reply})
    
    except Exception as e:
        return jsonify({"reply": f"*Dante se queda callado* (Error: {str(e)[:50]})"}), 500

if __name__ == '__main__':
    app.run(debug=True)




