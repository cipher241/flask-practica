from flask import Flask,request, jsonify, render_template
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
CONNECTION_STRING = os.getenv("CONN_STRING")
    
app = Flask(__name__)

def get_connection():
    return psycopg2.connect(CONNECTION_STRING)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/sensor')
def sensor():
    # Connect to the database
    try:
        connection = get_connection()
        print("Connection successful!")
        
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()
        
        # Example query
        cursor.execute("SELECT * from sensores")
        result = cursor.fetchone()
        print("Current Time:", result)
    
        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed.")
        return f"Current time: {result}"
    
    except Exception as e:
        print(f"Failed to connect: {e}")

@app.route("/sensor/<int:sensor_id>", methods=["POST"])
def insert_sensor_value(sensor_id):
    value = request.args.get("value", type=float)
    if value is None:
        return jsonify({"error": "Missing 'value' query parameter"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Insert into sensors table
        cur.execute(
            "INSERT INTO sensores (sensor_id, value) VALUES (%s, %s)",
            (sensor_id, value)
        )
        conn.commit()

        return jsonify({
            "message": "Sensor value inserted successfully",
            "sensor_id": sensor_id,
            "value": value
        }), 201

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if 'conn' in locals():
            conn.close()

@app.route("/sensor/<int:sensor_id>")
def get_sensor(sensor_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get the latest 10 values
        cur.execute("""
            SELECT value, created_at
            FROM sensores
            WHERE sensor_id = %s
            ORDER BY created_at DESC
            LIMIT 10;
        """, (sensor_id,))
        rows = cur.fetchall()

        # Convert to lists for graph
        values = [r[0] for r in rows][::-1]        # reverse for chronological order
        timestamps = [r[1].strftime('%Y-%m-%d %H:%M:%S') for r in rows][::-1]
        
        return render_template("sensor.html", sensor_id=sensor_id, values=values, timestamps=timestamps, rows=rows)

    except Exception as e:
        return f"<h3>Error: {e}</h3>"

    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/dashboard')
def dashboard():
    sensor_id = request.args.get("sensor_id", type=int)
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get the latest 10 values
        cur.execute("""
            SELECT DISTINCT sensor_id from sensores;;
        """)
        rows = cur.fetchall()
        values = [r[0] for r in rows]

        valores_sensor=None
        values_mostrar = None       
        timestamps_mostrar = None

        if sensor_id is not None:
            cur.execute("""
            SELECT value, created_at
            FROM sensores
            WHERE sensor_id = %s
            ORDER BY created_at DESC
            LIMIT 10;
            """, (sensor_id,))
            valores_sensor=cur.fetchall()

            print(valores_sensor)

            values_mostrar = [r[0] for r in rows][::-1]        # reverse for chronological order
            timestamps_mostrar = [r[1].strftime('%Y-%m-%d %H:%M:%S') for r in rows][::-1]
            
        return render_template("dashboard.html", rows=values, sensor_id = sensor_id, valores_sensor = valores_sensor, values_mostrar=values_mostrar, timestamps_mostrar=timestamps_mostrar)

    except Exception as e:
        return f"<h3>Error: {e}</h3>"

    finally:
        if 'conn' in locals():
            conn.close()