from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('aqi_data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    latitude REAL,
                    longitude REAL,
                    pm25 REAL,
                    co2 REAL,
                    humidity REAL,
                    temperature REAL,
                    aqi REAL,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

init_db()


def calculate_aqi(pm25, co2):
    aqi_pm25 = (pm25 / 500) * 100
    aqi_co2 = (co2 / 2000) * 100
    aqi = max(aqi_pm25, aqi_co2)
    return round(aqi, 2)


def row_to_dict(row):
    return {
        "id": row[0],
        "city": row[1],
        "latitude": row[2],
        "longitude": row[3],
        "pm25": row[4],
        "co2": row[5],
        "humidity": row[6],
        "temperature": row[7],
        "aqi": row[8],
        "timestamp": row[9]
    }



@app.route('/api/v1/aqi', methods=['POST'])
def add_reading():
    data = request.get_json()

    city = data.get('city')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    pm25 = data.get('pm25')
    co2 = data.get('co2')
    humidity = data.get('humidity')
    temperature = data.get('temperature')

    # Validate input
    if not all([city, pm25, co2, humidity, temperature]):
        return jsonify({"error": "Missing required fields"}), 400

    aqi = calculate_aqi(pm25, co2)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('aqi_data.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO readings 
                (city, latitude, longitude, pm25, co2, humidity, temperature, aqi, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (city, latitude, longitude, pm25, co2, humidity, temperature, aqi, timestamp))
    conn.commit()
    conn.close()

    return jsonify({
        "message": f"Data added successfully for {city}",
        "aqi": aqi,
        "timestamp": timestamp
    }), 201


@app.route('/api/v1/aqi/latest', methods=['GET'])
def get_latest():
    city = request.args.get('city')

    conn = sqlite3.connect('aqi_data.db')
    cur = conn.cursor()

    if city:
        cur.execute("SELECT * FROM readings WHERE city = ? ORDER BY id DESC LIMIT 1", (city,))
    else:
        cur.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1")

    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "No data found"}), 404

    return jsonify(row_to_dict(row))


@app.route('/api/v1/aqi/history', methods=['GET'])
def get_history():
    city = request.args.get('city')

    conn = sqlite3.connect('aqi_data.db')
    cur = conn.cursor()

    if city:
        cur.execute("SELECT * FROM readings WHERE city = ? ORDER BY id DESC LIMIT 10", (city,))
    else:
        cur.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 10")

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return jsonify({"error": "No data found"}), 404

    return jsonify([row_to_dict(row) for row in rows])


@app.route('/api/v1/aqi/cities', methods=['GET'])
def get_cities():
    """List all unique cities with their latest AQI"""
    conn = sqlite3.connect('aqi_data.db')
    cur = conn.cursor()
    cur.execute('''
        SELECT city, MAX(timestamp), aqi
        FROM readings
        GROUP BY city
        ORDER BY MAX(timestamp) DESC
    ''')
    rows = cur.fetchall()
    conn.close()

    cities = [{"city": r[0], "latest_aqi": r[2], "last_updated": r[1]} for r in rows]
    return jsonify(cities)


if __name__ == '__main__':
    app.run(debug=True)
