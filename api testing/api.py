from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/alihaider', methods=['GET'])
def hello_api():
    return jsonify({"message": "Hello, this is my first API and hello ALI HAIDER FORM BSCE 6!"})
@app.route('/AHMED', methods=['GET'])
def hello1_api():
    return jsonify({"message": "Hello, this is my first API and hello AHMED CGH FORM BSCE 6!"})
if __name__ == '__main__':
    app.run(debug=True)
