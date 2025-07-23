from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
#from openai import OpenAI
from data_cache import get_force_content
from flask import Flask, request, jsonify, send_file
import requests

app = Flask(__name__)
CORS(app)
# client = OpenAI(api_key="")  

full_text = get_force_content()


# def ask_gpt_force_n(message, context_text):
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "Tu es le porte-parole officiel du programme FORCE-N. "
#                 "Réponds uniquement à partir des données suivantes :\n\n"
#                 f"{context_text}\n\n"
#                 "Si tu ne trouves pas la réponse, dis simplement : "
#                 "'Je suis désolé, je n’ai pas cette information sur le site FORCE-N.' "
#                 "Utilise 'nous', sois institutionnel, sans supposition."
#             )
#         },
#         {
#             "role": "user",
#             "content": message
#         }
#     ]

#     response = client.chat.completions.create(
#         model="gpt-4",
#         messages=messages
#     )

#     return response.choices[0].message.content

def ask_gpt_force_n(message, context_text):
    prompt = (
        "Tu es le porte-parole officiel du programme FORCE-N.\n"
        "Réponds uniquement à partir des données suivantes :\n\n"
        f"{context_text}\n\n"
        f"Question : {message}\n\n"
        "Réponds de manière institutionnelle, sans inventer de contenu non mentionné dans les données."
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",  
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message")
    if not user_message:
        return jsonify({"error": "Message manquant"}), 400

    bot_response = ask_gpt_force_n(user_message, full_text)
    return jsonify({"response": bot_response})


@app.route("/")
def home():
    return send_file("index.html")

if __name__ == "__main__":
    app.run(debug=True)