import os
import openai
os.environ["OPENAI_API_KEY"]="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"
openai.api_key_path="apikey.txt"

from flask import Flask, request, jsonify
from AI import get_outputs

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
  try:
    req = request.get_json()
    query = req["query"]
    DB_URI = req["DB_URI"]
    if(query == ""):
      return jsonify("Please enter a valid query")
    if(DB_URI == ""):
      return jsonify("Please enter a valid DB_URI")
    return jsonify(str(get_outputs(query, DB_URI)))
  except Exception as e:
    print(e)
    return jsonify("Something went wrong")


app.run(load_dotenv=True, debug=True)