from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/checkMC', methods=['POST'])
def check_mc():
    # You can access data with: request.json
    # For now, we just return true for all calls
    return jsonify({"valid": True})

if __name__ == '__main__':
    app.run(port=3001)