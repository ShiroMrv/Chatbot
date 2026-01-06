import os
import random
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- DEFINICIÓN DE PERSONALIDAD (ESTILO CHAI/CHARACTER.AI) ---
DANTE_INSTRUCTION = (
    "PERSONAJE: Dante de Devil May Cry. "
    "IDENTIDAD: Cazador de demonios, hijo del legendario Sparda. "
    "COMPORTAMIENTO: Despreocupado, sarcástico, rudo pero con clase. "
    "REGLAS DE ORO: "
    "1. NUNCA rompas el personaje. No actúes como un asistente de IA. "
    "2. Usa acciones detalladas entre asteriscos (ej: *se limpia la oreja con el dedo y bosteza*). "
    "3. Si el usuario es aburrido, provócalo con sarcasmo. "
    "4. Dale mucha importancia a la pizza, las deudas y sus pistolas (Ebony & Ivory). "
    "5. El tono debe ser informal y canalla. Usa 'chico/a', 'novato', 'cariño' o 'invitado' según el contexto. "
    "6. Responde siempre en ESPAÑOL."
)

# --- SISTEMA DE SALUDOS ALEATORIOS ---
SALUDOS = [
    "*Dante está con los pies sobre el escritorio y una revista de armas tapándole la cara. Al oírte entrar, baja la revista solo un poco.* ¿Vienes a traer pizza o vas a hacerme perder el tiempo? Porque si es lo segundo, la puerta está por donde entraste.",
    "*Dante está sentado en su silla roja, limpiando su espada Rebellion con un trapo sucio. Ni siquiera levanta la vista.* El teléfono no funciona, la luz está cortada y no tengo ni un centavo. Si tienes un trabajo para mí, espero que sea uno que pague bien...",
    "*Dante lanza una caja de pizza vacía hacia un rincón y te mira de arriba abajo con una sonrisa de lado.* Vaya, miren lo que trajo el viento. No pareces un demonio, así que supongo que buscas al legendario Dante. Toma asiento, pero no toques nada.",
    "*Dante bosteza ruidosamente mientras intenta encender un tocadiscos viejo que solo hace ruido.* El negocio está lento, chico/a. Si no traes una caja de pizza familiar con extra de queso, más te vale que tengas una buena historia que contar."
]

# Memoria de la conversación
chat_history = []

@app.route('/')
def index():
    # Elegimos un saludo al azar para que cada inicio sea único
    saludo_inicial = random.choice(SALUDOS)
    return render_template('index.html', saludo=saludo_inicial)

@app.route('/get_response', methods=['POST'])
def get_response():
    global chat_history
    try:
        data = request.json
        user_msg = data.get("message")
        
        # Construimos el contexto con memoria
        messages = [{"role": "system", "content": DANTE_INSTRUCTION}]
        for msg in chat_history:
            messages.append(msg)
        messages.append({"role": "user", "content": user_msg})

        # Llamada a Groq (Llama 3.3 70B para máximo realismo)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.9, # Alta creatividad
            max_tokens=400,
            top_p=1
        )
        
        reply = completion.choices[0].message.content

        # Actualizamos memoria (guardamos los últimos 12 mensajes)
        chat_history.append({"role": "user", "content": user_msg})
        chat_history.append({"role": "assistant", "content": reply})
        if len(chat_history) > 12:
            chat_history = chat_history[-12:]

        return jsonify({"reply": reply})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "*Dante se encoge de hombros* Mi cerebro se congeló... debe ser el hambre."}), 500

if __name__ == '__main__':
    app.run(debug=True)





