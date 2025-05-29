from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/checkMC', methods=['POST'])
def check_mc():
    data = request.get_json()
    if data and "MC_num" in data and data["MC_num"] == "12345678":
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3001)