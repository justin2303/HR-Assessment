from flask import Flask, request, jsonify
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
    if data and "MC_num" in data and data["MC_num"] == "12345678":
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})
    
@app.route('/fetchLoad', methods=['POST'])
def fetchLoad():
    data = request.get_json()
    if not data or not "Location" in data or not "Minimum_Date" in data or not "Equipment" in data:
        return jsonify({"error": True})
    conn = mysql.connector.connect(
        host="localhost",    
        user="root",  
        password="Happy",
        database="loadDB"
    )
    dt_obj = datetime.strptime(data["Minimum_Date"], "%A, %B %d, %Y at %I:%M:%S %p")
    sql_datetime = dt_obj.strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM loads_template
        WHERE origin LIKE %s
        AND equipment_type LIKE %s
        AND pickup_datetime > %s
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