import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Dairy Milk Collection", page_icon="🥛", layout="wide")

DB_FILE = "dairy_database.csv"

# Load existing data if available
if os.path.exists(DB_FILE):
    df_entries = pd.read_csv(DB_FILE)
else:
    df_entries = pd.DataFrame(columns=[
        "Date", "Farmer", "Shift", "Animal", "Liters", "FAT", "SNF", "Rate/L", "Total Amount"
    ])

st.title("🥛 Dairy Milk Collection & Billing System")

# --- SIDEBAR : RATE CHART SETTINGS ---
st.sidebar.header("⚙️ Rate Chart Settings")

animal_type = st.sidebar.radio("Select Settings For", ["Cow Settings", "Buffalo Settings"])

if animal_type == "Cow Settings":
    st.sidebar.subheader("🐮 Cow Rate Parameters")
    cow_base_rate = st.sidebar.number_input("Cow Base Rate (for 3.5 FAT / 8.5 SNF)", min_value=1.0, max_value=100.0, value=35.0, step=0.5)
    cow_fat_step = st.sidebar.slider("Cow FAT Diff Rate per 0.1% (₹0.10 - ₹0.50)", min_value=0.10, max_value=0.50, value=0.30, step=0.05)
    cow_snf_step = st.sidebar.slider("Cow SNF Diff Rate per 0.1% (₹0.10 - ₹0.50)", min_value=0.10, max_value=0.50, value=0.20, step=0.05)
    buff_base_rate, buff_fat_step, buff_snf_step = 60.0, 0.50, 0.30
else:
    st.sidebar.subheader("🦬 Buffalo Rate Parameters")
    buff_base_rate = st.sidebar.number_input("Buffalo Base Rate (for 6.0 FAT / 9.0 SNF)", min_value=1.0, max_value=200.0, value=60.0, step=0.5)
    buff_fat_step = st.sidebar.slider("Buffalo FAT Diff Rate per 0.1% (₹0.10 - ₹0.80)", min_value=0.10, max_value=0.80, value=0.50, step=0.05)
    buff_snf_step = st.sidebar.slider("Buffalo SNF Diff Rate per 0.1% (₹0.10 - ₹0.80)", min_value=0.10, max_value=0.80, value=0.30, step=0.05)
    cow_base_rate, cow_fat_step, cow_snf_step = 35.0, 0.30, 0.20

st.sidebar.markdown("---")
st.sidebar.header("📝 Daily Milk Entry")

farmer_name = st.sidebar.text_input("Farmer Name / Code")
shift = st.sidebar.selectbox("Shift", ["Morning", "Evening"])
selected_animal = st.sidebar.selectbox("Animal", ["Cow", "Buffalo"])
liters = st.sidebar.number_input("Liters", min_value=0.1, max_value=500.0, value=5.0, step=0.5)

if selected_animal == "Cow":
    fat = st.sidebar.number_input("FAT % (Cow)", min_value=2.0, max_value=10.0, value=3.5, step=0.1)
    snf = st.sidebar.number_input("SNF % (Cow)", min_value=6.0, max_value=12.0, value=8.5, step=0.1)
else:
    fat = st.sidebar.number_input("FAT % (Buffalo)", min_value=3.0, max_value=15.0, value=6.0, step=0.1)
    snf = st.sidebar.number_input("SNF % (Buffalo)", min_value=6.0, max_value=12.0, value=9.0, step=0.1)

date_entry = st.sidebar.date_input("Date", datetime.today())

def calculate_standard_rate(animal, fat_val, snf_val):
    if animal == "Cow":
        base_fat, base_snf = 3.5, 8.5
        base_rate, fat_diff_rate, snf_diff_rate = cow_base_rate, cow_fat_step, cow_snf_step
    else:
        base_fat, base_snf = 6.0, 9.0
        base_rate, fat_diff_rate, snf_diff_rate = buff_base_rate, buff_fat_step, buff_snf_step

    fat_diff = round((fat_val - base_fat) * 10, 2)
    snf_diff = round((snf_val - base_snf) * 10, 2)
    final_rate = base_rate + (fat_diff * fat_diff_rate) + (snf_diff * snf_diff_rate)
    return max(0.0, round(final_rate, 2))

calculated_rate = calculate_standard_rate(selected_animal, fat, snf)
total_amount = round(calculated_rate * liters, 2)

st.sidebar.info(f"💡 **Rate/Liter:** ₹{calculated_rate}\n\n💰 **Total Amount:** ₹{total_amount}")

if st.sidebar.button("Save Entry"):
    if farmer_name.strip() != "":
        new_entry = pd.DataFrame([{
            "Date": date_entry.strftime("%Y-%m-%d"),
            "Farmer": farmer_name,
            "Shift": shift,
            "Animal": selected_animal,
            "Liters": liters,
            "FAT": fat,
            "SNF": snf,
            "Rate/L": calculated_rate,
            "Total Amount": total_amount
        }])
        
        df_entries = pd.concat([df_entries, new_entry], ignore_index=True)
        df_entries.to_csv(DB_FILE, index=False)
        st.sidebar.success("Entry Permanently Saved!")
        st.rerun()
    else:
        st.sidebar.error("Please enter Farmer Name!")

# --- MAIN DASHBOARD ---
st.subheader("📋 Collection History")

if not df_entries.empty:
    st.dataframe(df_entries, use_container_width=True)
    
    st.markdown("---")
    st.subheader("💰 10-Day Payment Summary")
    
    summary = df_entries.groupby("Farmer").agg(
        Total_Liters=("Liters", "sum"),
        Total_Payment=("Total Amount", "sum")
    ).reset_index()
    
    st.table(summary)
    
    csv = df_entries.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Backup Excel/CSV", data=csv, file_name="milk_collection_backup.csv", mime="text/csv")
    
    if st.button("⚠️ Clear All Records"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            st.rerun()
else:
    st.info("No collection entries found. Add entries using the sidebar.")
