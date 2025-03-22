# database.py
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai
from utils import format_date, clean_amount


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "checkmate")
    )


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cheques (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cheque_number VARCHAR(50),
            account_number VARCHAR(50),
            bank_name VARCHAR(100),
            payee VARCHAR(100),
            amount FLOAT,
            date VARCHAR(50)
        )
    ''')
    conn.commit()
    conn.close()

def cheque_exists(cheque_number):
    cheque_number = cheque_number.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cheques WHERE UPPER(TRIM(cheque_number)) = %s", (cheque_number,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def insert_cheque_details(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        formatted_date = format_date(data.get("cheque_date", ""))
    except ValueError as e:
        raise ValueError(f"🚨 Invalid cheque date: {data.get('cheque_date')}. Error: {e}")
    cheque_amount = clean_amount(data.get("amount", ""))
    query = '''INSERT INTO cheques (cheque_number, account_number, bank_name, payee, amount, date) 
               VALUES (%s, %s, %s, %s, %s, %s)'''
    values = (
        data.get("cheque_number", ""),
        data.get("account_number", ""),
        data.get("bank_name", ""),
        data.get("payee_name", ""),
        cheque_amount,
        formatted_date
    )
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def fetch_all_records():
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM cheques", conn)
    conn.close()
    return df
