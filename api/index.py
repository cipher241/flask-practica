from flask import Flask
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
