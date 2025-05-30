from flask import Flask, request, jsonify
import requests
import random
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
        url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{data["MC_num"]}?webKey={api_key}"
        response = requests.get(url)
        data = response.json()
        if data["content"] == []:
            sessionID, sessionCode = createSessionID()
            return jsonify({"valid": False, "sessionID": sessionID,"sessionCode": sessionCode})
        else:
            return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})
    
@app.route('/fetchLoad', methods=['POST'])
def fetchLoad():
    data = request.get_json()
    if not data or not "Location" in data or not "Equipment" in data:
        return jsonify({"error": True})
    if "sessionID" not in data or "sessionCode" not in data:
        return jsonify({"error": True})
    conn = mysql.connector.connect(
        host="localhost",    
        user="root",  
        password="Happy",
        database="loadDB"
    )
    if not verifySession(data["sessionID"], data["sessionCode"], conn):
        return jsonify({"error": True})
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

def createSessionID():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Robots",
        database="loadDB"
    )
    cursor = conn.cursor()
    session_code = ''.join(str(random.randint(0, 9)) for _ in range(8))
    created_when = datetime.now()
    insert_query = """
        INSERT INTO session_table (session_code, created_when)
        VALUES (%s, %s)
    """
    cursor.execute(insert_query, (session_code, created_when))
    session_id = cursor.lastrowid #threadsafe apparently
    cursor.close()
    conn.close()
    return session_code,session_id


def verifySession(sessionID, sessionCode, conn):
    cursor = conn.cursor()
    query = """
        SELECT * FROM session_table
        WHERE session_id = %s
        AND session_code = %s
        LIMIT 1
    """
    cursor.execute(query, (sessionID, sessionCode))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return True
    else:
        return False