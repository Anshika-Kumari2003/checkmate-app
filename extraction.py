# extraction.py
import io
import json
from PIL import Image
import google.generativeai as genai
from utils import format_date

def extract_cheque_data(image_bytes):
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = """Extract details from the cheque and return a JSON object with the following fields:
        {
            "cheque_number": "",
            "account_number": "",
            "bank_name": "",
            "payee_name": "",
            "amount": "",
            "cheque_date": ""
        }
    """
    image = Image.open(io.BytesIO(image_bytes))
    response = model.generate_content([prompt, image])
    if not hasattr(response, "text") or not response.text.strip():
        raise ValueError("❌ API returned an empty response.")
    # Clean response text by removing markdown formatting and any leading "json" prefix.
    response_text = response.text.strip().replace("```json", "").replace("```", "")
    if response_text.lower().startswith("json"):
        response_text = response_text[4:].strip()
    try:
        cheque_data = json.loads(response_text)
        if "cheque_date" in cheque_data:
            cheque_data["cheque_date"] = format_date(cheque_data["cheque_date"])
        return cheque_data
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ Failed to parse JSON response: {e}\nResponse Text: {response_text}")
