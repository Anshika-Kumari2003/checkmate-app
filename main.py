# main.py
import streamlit as st
import os
import io
from PIL import Image
from pdf2image import convert_from_bytes
import pandas as pd
import plotly.express as px

# Import our modules
#from config import API_KEY
from utils import format_date, clean_amount
from database import API_KEY,create_table, cheque_exists, insert_cheque_details, fetch_all_records
from extraction import extract_cheque_data

# Initialize the database
create_table()

st.set_page_config(page_title="CheckMate", layout="wide")
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { background-color: #D3D3D3 !important; }
        [data-testid="stSidebar"] * { color: black !important; }
        [data-testid="stSidebarNav"] button:hover { background-color: #BEBEBE !important; }
        .stApp { background-color: #FFFFFF !important; color: black !important; }
        input, textarea, select { background-color: #F5F5F5 !important; color: black !important; }
        .stButton>button { background-color: #004aad !important; color: white !important; border-radius: 8px; }
        .stButton>button:hover { background-color: #003080 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📤 Upload", "📊 Dashboard", "📈 Analytics"])

if page == "🏠 Home":
    st.markdown("<h1 style='text-align: center; color: #004aad; font-size: 36px;'>🏦 CheckMate: AI-Powered Cheque Processing</h1>", unsafe_allow_html=True)
    st.write("### 📌 Transforming cheque processing with AI and automation!")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 💡 Why Choose CheckMate?")
        st.markdown("""
            - ✅ **Automated cheque processing** – No manual data entry needed.
            - 🤖 **AI-powered data extraction** – Reads and understands cheque details.
            - 🔒 **Secure & Fast** – Your data is encrypted and processed instantly.
            - 📊 **Detailed analytics** – Get insights into cheque transactions.
            - 🏦 **Multi-bank support** – Works with all major banks.
        """)
    with col2:
        image_path = r"H:\CheckMate Automated Bank Check Processor.webp"
        try:
            st.image(image_path, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error loading image: {e}")
    st.markdown("---")
    st.markdown("### 🌟 Key Features of CheckMate")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.markdown("📝 **OCR Scanning**")
        st.write("Extracts text from scanned cheques with high accuracy.")
    with col4:
        st.markdown("📊 **Analytics Dashboard**")
        st.write("Gain insights into cheque transactions with visual charts.")
    with col5:
        st.markdown("🔄 **Bulk Processing**")
        st.write("Upload multiple cheques at once for faster processing.")
    st.markdown("---")
    st.markdown("<p style='text-align: center;'>© 2025 CheckMate | Secure AI-Powered Cheque Processing</p>", unsafe_allow_html=True)

elif page == "📤 Upload":
    st.title("📄 Upload Cheque PDF(s) or Image(s)")
    upload_files = st.file_uploader("Upload Cheque(s)", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)
    if upload_files:
        for idx, upload_file in enumerate(upload_files):
            st.markdown(f"### Processing file: {upload_file.name}")
            # Convert PDF to image if needed
            if upload_file.type == "application/pdf":
                try:
                    images = convert_from_bytes(upload_file.getvalue(), first_page=1, last_page=1)
                    image = images[0].convert("RGB")
                except Exception as e:
                    st.error(f"❌ Failed to convert PDF: {upload_file.name}. Error: {e}")
                    continue
            else:
                try:
                    image = Image.open(upload_file)
                except Exception as e:
                    st.error(f"❌ Failed to open image: {upload_file.name}. Error: {e}")
                    continue

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            image_bytes = img_byte_arr.getvalue()
            st.image(image, caption=f"Uploaded Cheque: {upload_file.name}", use_container_width=True)
            
            # Use a unique key for each button
            if st.button(f"📌 Extract Data from {upload_file.name}", key=f"extract_{idx}_{upload_file.name}"):
                with st.spinner("Extracting details..."):
                    try:
                        cheque_data = extract_cheque_data(image_bytes)
                        cheque_num = cheque_data.get("cheque_number", "").strip().upper()
                        if cheque_num and cheque_exists(cheque_num):
                            st.warning(f"⚠️ Cheque {cheque_num} has already been processed!")
                        else:
                            st.json(cheque_data)
                            insert_cheque_details(cheque_data)
                            st.success(f"✅ Data saved successfully for {upload_file.name}!")
                    except ValueError as e:
                        st.warning(str(e))

elif page == "📊 Dashboard":
    st.title("📊 Cheque Dashboard")
    df = fetch_all_records()
    if df.empty:
        st.warning("No records found.")
    else:
        total_cheques = len(df)
        total_amount = df["amount"].sum()
        avg_amount = df["amount"].mean()
        col1, col2, col3 = st.columns(3)
        col1.metric("📄 Total Cheques", total_cheques)
        col2.metric("💰 Total Amount", f"${total_amount:,.2f}")
        col3.metric("📊 Avg Cheque Amount", f"${avg_amount:,.2f}")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode()
        json_data = df.to_json(orient="records")
        st.download_button("📥 Download CSV", csv, "cheques_data.csv", "text/csv")
        st.download_button("📥 Download JSON", json_data, "cheques_data.json", "application/json")
        st.markdown("---")
        st.subheader("📊 Data Insights")
        col4, col5 = st.columns(2)
        with col4:
            st.subheader("Top Payees")
            top_payees = df["payee"].value_counts().head(5)
            fig = px.bar(top_payees, x=top_payees.index, y=top_payees.values, labels={"x": "Payee", "y": "Count"}, title="Top 5 Payees")
            st.plotly_chart(fig, use_container_width=True)
        with col5:
            st.subheader("Top Banks")
            top_banks = df["bank_name"].value_counts().head(5)
            fig = px.bar(top_banks, x=top_banks.index, y=top_banks.values, labels={"x": "Bank", "y": "Count"}, title="Top 5 Banks")
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("📅 Transactions Over Time")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df_filtered = df.dropna(subset=["date"])
        if not df_filtered.empty:
            df_filtered["date"] = df_filtered["date"].dt.date
            date_counts = df_filtered.groupby("date")["id"].count().reset_index()
            date_counts.columns = ["Date", "Number of Transactions"]
            fig = px.line(date_counts, x="Date", y="Number of Transactions", markers=True, title="Transactions Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid date data available for trend analysis.")

elif page == "📈 Analytics":
    st.title("📈 Cheque Analytics")
    df = fetch_all_records()
    if df.empty:
        st.warning("No records to analyze.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Amount Distribution")
            fig = px.histogram(df, x="amount", nbins=20, title="Cheque Amount Distribution", color_discrete_sequence=['#1f77b4'])
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Bank-wise Transactions")
            fig = px.pie(df, names="bank_name", title="Cheques by Bank", hole=0.3, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
