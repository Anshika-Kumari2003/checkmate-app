import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai
from utils import format_date, clean_amount

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
genai.configure(api_key=API_KEY)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def cheque_exists(cheque_number):
    """Checks if a cheque number already exists in the database."""
    cheque_number = cheque_number.strip().upper()
    response = supabase.table("cheques").select("id").eq("cheque_number", cheque_number).execute()
    return len(response.data) > 0


def insert_cheque_details(data):
    """Inserts cheque details into the database."""
    try:
        formatted_date = format_date(data.get("cheque_date", ""))
    except ValueError as e:
        raise ValueError(f"🚨 Invalid cheque date: {data.get('cheque_date')}. Error: {e}")

    cheque_amount = clean_amount(data.get("amount", ""))

    values = {
        "cheque_number": data.get("cheque_number", ""),
        "account_number": data.get("account_number", ""),
        "bank_name": data.get("bank_name", ""),
        "payee": data.get("payee_name", ""),
        "amount": cheque_amount,
        "date": formatted_date,
    }

    # Do not manually insert 'id'
    response = supabase.table("cheques").insert(values).execute()
    return response



def fetch_all_records():
    """Fetches all records from the database and returns as a DataFrame."""
    response = supabase.table("cheques").select("*").execute()
    return pd.DataFrame(response.data)
