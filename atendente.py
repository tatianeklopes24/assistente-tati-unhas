import os
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# Inicializa o cliente do Gemini utilizando a variável de ambiente GEMINI_API_KEY
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Prompt do sistema com as diretrizes da assistente Tati Lopes Nails
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
    # Suporte para validação via GET (caso o gateway de WhatsApp exija verificação)
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge') or request.args.get('challenge')
        if challenge:
            return challenge, 200
        return "Webhook ativo e aguardando requisições POST.", 200

    # Tratamento flexível do JSON no POST para evitar erro 400 (Bad Request)
    data = request.get_json(silent=True) or {}
    
    # Extrai o texto da mensagem enviada em diferentes formatos comuns de integradores
    user_message = (
        data.get('message') or 
        data.get('text') or 
        data.get('body') or 
        (data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0].get('text', {}).get('body'))
    )

    if not user_message:
        return jsonify({"status": "ignored", "reason": "Nenhuma mensagem de texto válida encontrada"}), 200

    try:
        # Gera a resposta utilizando a biblioteca nova do Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config={
                "system_instruction": SYSTEM_INSTRUCTION
            }
        )

        reply_text = response.text

        # Retorna a resposta formatada
        return jsonify({
            "status": "success",
            "response": reply_text
        }), 200

    except Exception as e:
        print(f"Erro ao processar mensagem com Gemini: {e}")
        return jsonify({
            "status": "error",
            "message": "Ocorreu um erro interno ao processar a resposta."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)