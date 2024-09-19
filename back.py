from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv, find_dotenv

app = Flask(__name__)

# Carregar variáveis de ambiente
_ = load_dotenv(find_dotenv())

# Requisição para a API da OpenAI
@app.route("/ask", methods=["POST"])
def ask_openai():
    data = request.json
    question = data.get("question", "")
    
    if question:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({'answer': answer})
    else:
        return jsonify({"error": "Nenhuma pergunta fornecida"}), 400

if __name__ == "__main__":
    app.run(debug=True)