import sys
import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Pega a chave da API das variáveis de ambiente com segurança
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else genai.Client()

# Carrega a base de dados do salão
try:
    with open("base_conhecimento.txt", "r", encoding="utf-8") as file:
        base_conhecimento = file.read()
except FileNotFoundError:
    base_conhecimento = "Estúdio Tati Lopes Nails - Atendimento privativo com horário marcado."

instrucoes = f"""
Você é a assistente virtual atenciosa do estúdio Tati Lopes Nails.
Sua função é atender clientes no WhatsApp de forma muito amigável, tirar dúvidas e organizar os agendamentos.

Consulte SEMPRE a base de conhecimento abaixo para responder:
{base_conhecimento}
"""

config = types.GenerateContentConfig(system_instruction=instrucoes)
chat = client.chats.create(model="gemini-3.8-flash", config=config)

@app.route("/", methods=["GET"])
def home():
    return "Servidor da Assistente Tati Lopes Nails está online!", 200

# Rota Webhook que receberá as mensagens do WhatsApp
@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.get_json() or {}
    
    # Extrai a mensagem recebida do WhatsApp
    mensagem_cliente = dados.get("message", "")
    
    if mensagem_cliente:
        try:
            resposta = chat.send_message(mensagem_cliente)
            return jsonify({"status": "sucesso", "resposta": resposta.text})
        except Exception as e:
            return jsonify({"status": "erro", "detalhe": str(e)}), 500
    
    return jsonify({"status": "sem mensagem"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)