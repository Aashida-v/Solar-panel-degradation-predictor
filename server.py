from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load EMAIL, PASSWORD, API keys from .env

app = Flask(__name__)

# Load API key from .env
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

@app.route("/geocode")
def geocode():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    url = f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={OPENCAGE_API_KEY}"
    r = requests.get(url)
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(debug=True)