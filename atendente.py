import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configura a API Key do Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_INSTRUCTION = """
Você é a assistente virtual do estúdio de unhas Tati Lopes Nails (@tati_lopesnails).
Seu objetivo é atender clientes de forma acolhedora, profissional e eficiente.
Forneça informações sobre horários disponíveis, serviços de manicure/nail design e ajude no agendamento.
Mantenha o tom simpático, claro e objetivo.
"""

@app.route('/', methods=['GET'])
def home():
    return "Servidor da Assistente Tati Lopes Nails está online!", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge') or request.args.get('challenge')
        if challenge:
            return challenge, 200
        return "Webhook ativo e aguardando requisições POST.", 200

    data = request.get_json(silent=True) or {}
    
    user_message = (
        data.get('message') or 
        data.get('text') or 
        data.get('body') or 
        (data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text', {}).get('body'))
    )

    if not user_message:
        return jsonify({"status": "ignored", "reason": "Nenhuma mensagem enviada"}), 200

    if not api_key:
        return jsonify({
            "status": "error",
            "message": "Variável GEMINI_API_KEY não encontrada no servidor."
        }), 500

    try:
        # Usa o modelo gemini-2.5-flash (compatível e ativo na v1beta)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        response = model.generate_content(user_message)

        return jsonify({
            "status": "success",
            "response": response.text
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)