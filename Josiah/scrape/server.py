from flask import jsonify
import json
from flask import Flask
app = Flask(__name__)

@app.route("/comments")
def comments():
    with open("latlng.json") as f:
        data = f.read()
    return jsonify(json.loads(data))

@app.route("/success")
def success():
    with open("success.json") as f:
        data = f.read()
    return jsonify(json.loads(data))
