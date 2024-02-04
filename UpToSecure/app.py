from flask import Flask, jsonify, request
from flask_cors import CORS
from SerpAI import up_to_secure

app = Flask(__name__)

CORS(app)

@app.route('/api/secure', methods=['POST'])
def secure():
    data = request.get_json()
    response = up_to_secure.query(data['text'])
    return jsonify(response)