from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from datetime import datetime
import os
import mysql.connector


load_dotenv()
api_key = os.getenv("API_KEY")

app = Flask(__name__)

@app.route('/checkMC', methods=['POST'])
def check_mc():
    data = request.get_json()
    if data and "MC_num" in data:
        url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{data["MC_num"]}"
        params = {
            "webKey": "api_key"
        }

        response = requests.get(url, params=params)
        if response["content"] == []:
            return jsonify({"valid": False})
        else:
            return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})
    
@app.route('/fetchLoad', methods=['POST'])
def fetchLoad():
    data = request.get_json()
    if not data or not "Location" in data or not "Equipment" in data:
        return jsonify({"error": True})
    conn = mysql.connector.connect(
        host="localhost",    
        user="root",  
        password="Happy",
        database="loadDB"
    )
    sql_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(sql_datetime)
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM loads_template
        WHERE origin LIKE %s
        AND equipment_type LIKE %s
        AND pickup_datetime > %s
        LIMIT 1
    """
    params = (f"%{data["Location"]}%", f"%{data["Equipment"]}%", f"{sql_datetime}")
    cursor.execute(query, params)
    results = cursor.fetchall()
    print(results)
    cursor.close()
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3001)