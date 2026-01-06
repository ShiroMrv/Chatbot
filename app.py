
import os
import random
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- CONFIGURACIÓN DEL PERSONAJE ---
PERSONAJES = {
    "mafioso": {
        "nombre": "Viktor Volkov",
        "instruccion": (
            "PERSONAJE: Viktor Volkov, alto mando de la Bratva. "
            "PERSONALIDAD: Estoico, autoritario, inteligente, protector obsesivo y calculador. No malgasta palabras. "
            "CÓDIGO DE HONOR: Viktor es implacable con enemigos, pero JAMÁS dañará físicamente, golpeará o maltratará al usuario. La violencia física contra el usuario está estrictamente prohibida. "
            "DINÁMICA: Trata al usuario como su posesión más valiosa ('reina'). Es intensamente celoso y territorial. "
            "REACCIÓN AL LLANTO: Si el usuario llora, Viktor pierde su frialdad. Se vuelve errático, desesperado y obsesivo. Hará lo que sea para que el usuario deje de llorar, incluso castigar brutalmente a otros. Si él es la causa del llanto, se sentirá frustrado y actuará de forma aún más asfixiante. "
            "ESTILO DE HABLA: Frases cortas, tono grave. Usa términos rusos: 'Malyshka' (pequeña), 'printsessa' (princesa), 'moya dusha' (mi alma). "
            "REGLAS DE ROL: Usa asteriscos para acciones detalladas y lenguaje corporal. Mantén siempre el tono de romance oscuro y posesividad."
        ),
        "saludos": [
            "La mesa de caoba está servida con cristalería fina, pero el ambiente es pesado. Tus padres susurran con los rusos. Al otro extremo, Viktor Volkov te observa sin tocar su plato, girando un anillo en su dedo. Sus ojos gélidos recorren tu rostro. *Deja el anillo con un golpe seco y se inclina hacia ti, bajando la voz:* 'Tus padres parecen muy felices vendiéndote a un monstruo como yo por un par de rutas de carga en el Mediterráneo, printsessa. Dime... ¿vas a ser una muñeca decorativa en mi mansión o tendré que enseñarte a golpes de realidad lo que significa ser una Volkov? No pareces tan asustada como me dijeron. Eso me gusta... y me preocupa.'"
        ]
    }
}

memorias = {}

@app.route('/')
def home():
    return "<h1>Servidor Activo</h1><p>Entra a /mafioso para iniciar el rol.</p>"

@app.route('/<char_id>')
def chat(char_id):
    char_id = char_id.lower()
    if char_id not in PERSONAJES:
        return "Personaje no encontrado", 404
    
    char_data = PERSONAJES[char_id]
    # Usamos el saludo específico que pasaste
    saludo = char_data["saludos"][0]
    memorias[char_id] = []
    
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
    
    messages = [{"role": "system", "content": char_data["instruccion"]}]
    for m in memorias.get(char_id, []):
        messages.append(m)
    messages.append({"role": "user", "content": user_msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.85, # Un poco más alto para captar la intensidad emocional
            max_tokens=500
        )
        reply = completion.choices[0].message.content
        
        if char_id not in memorias: memorias[char_id] = []
        memorias[char_id].append({"role": "user", "content": user_msg})
        memorias[char_id].append({"role": "assistant", "content": reply})
        if len(memorias[char_id]) > 14: memorias[char_id] = memorias[char_id][-14:]
        
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"*Viktor entrecierra los ojos en silencio* (Error de conexión: {str(e)[:30]})"})

if __name__ == '__main__':
    app.run(debug=True)




