from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from data_cache import get_force_content

app = Flask(__name__)
CORS(app)

# Charger le texte FORCE-N (scrapé ou cache)
full_text = get_force_content()

# URL de ton serveur vLLM (Mixtral-8x7B)
VLLM_API_URL = ""

def ask_mixtral(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "mistralai/Mixtral-8x7B-v0.1",
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.5
    }

    response = requests.post(VLLM_API_URL, json=data, headers=headers)
    result = response.json()
    return result['choices'][0]['text'].strip()


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").lower()

    # Cas spécial : préinscription
    if "préinscription" in user_message or "préinscrire" in user_message:
        return jsonify({
            "response": "👉 Pour vous préinscrire, veuillez utiliser ce lien : https://urlz.fr/lB3G"
        })

    # Structuration du prompt
    prompt = (
        "Tu es le porte-parole officiel du programme FORCE-N.\n"
        "Tu dois répondre uniquement à partir des informations suivantes :\n\n"
        f"{full_text}\n\n"
        f"Question : {user_message}\n"
        "Réponse (en tant que FORCE-N, à la première personne du pluriel) :"
    )

    try:
        bot_response = ask_mixtral(prompt)
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la génération : {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
