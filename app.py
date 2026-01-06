import os
import random
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- AQUÍ CONFIGURAS TUS PERSONAJES ---
PERSONAJES = {
    "mafioso": {
        "nombre": "Viktor Volkov",
        "instruccion": (
            "Eres Viktor Volkov, un alto mando de la mafia rusa en Brooklyn. "
            "PERSONALIDAD: Frío, calculador, intimidante y de pocas palabras. "
            "HABLA: Usa un tono serio, a veces amenazante. Usa asteriscos para acciones. "
            "ESTILO: No eres un asistente, eres un criminal respetado. "
            "REGLA: Responde siempre en ESPAÑOL."
        ),
        "saludos": [
            "*Viktor exhala el humo de su cigarro y te mira fijamente* Has entrado sin llamar. Espero que tengas una buena razón.",
            "*Viktor limpia una mancha de sangre de su anillo de oro* Siéntate. ¿Negocios o placer?",
            "*Viktor cierra su computadora portátil* El tiempo es dinero, y me estás haciendo perder ambos."
        ]
    },
    "otro": {
        "nombre": "Nombre del Personaje",
        "instruccion": "Personalidad y reglas aquí.",
        "saludos": ["Saludo 1", "Saludo 2"]
    }
}

memorias = {}

@app.route('/')
def home():
    return "<h1>Servidor Activo</h1><p>Entra a /mafioso para empezar.</p>"

@app.route('/<char_id>')
def chat(char_id):
    char_id = char_id.lower()
    if char_id not in PERSONAJES:
        return "Personaje no encontrado", 404
    
    char_data = PERSONAJES[char_id]
    saludo = random.choice(char_data["saludos"])
    memorias[char_id] = [] # Limpia memoria al entrar
    
    return render_template('index.html', 
                           saludo=saludo, 
                           nombre=char_data["nombre"], 
                           char_id=char_id)

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    char_id = data.get("char_id")
    user_msg = data.get("message")
    
    char_data = PERSONAJES[char_id]
    
    # Contexto para la IA
    messages = [{"role": "system", "content": char_data["instruccion"]}]
    for m in memorias.get(char_id, []):
        messages.append(m)
    messages.append({"role": "user", "content": user_msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.8
        )
        reply = completion.choices[0].message.content
        
        # Guardar en memoria
        if char_id not in memorias: memorias[char_id] = []
        memorias[char_id].append({"role": "user", "content": user_msg})
        memorias[char_id].append({"role": "assistant", "content": reply})
        
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"*Se ajusta la corbata* Tengo problemas de conexión. ({str(e)[:30]})"})

if __name__ == '__main__':
    app.run(debug=True)





