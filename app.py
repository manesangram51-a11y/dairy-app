import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Mane Dairy Collection System", page_icon="🥛", layout="wide")

# Initialize session state for entries
if "entries" not in st.session_state:
    st.session_state.entries = []

st.title("🥛 Dairy Milk Collection & Billing System")

# --- SIDEBAR : RATE CHART SETTINGS ---
st.sidebar.header("⚙️ Rate Chart Settings")

animal_type = st.sidebar.radio("Select Settings For", ["Cow Settings", "Buffalo Settings"])

if animal_type == "Cow Settings":
    st.sidebar.subheader("🐮 Cow Rate Parameters")
    cow_base_rate = st.sidebar.number_input("Cow Base Rate (for 3.5 FAT / 8.5 SNF)", min_value=1.0, max_value=100.0, value=35.0, step=0.5)
    cow_fat_step = st.sidebar.slider("Cow FAT Diff Rate per 0.1% (₹0.10 - ₹0.50)", min_value=0.10, max_value=0.50, value=0.30, step=0.05)
    cow_snf_step = st.sidebar.slider("Cow SNF Diff Rate per 0.1% (₹0.10 - ₹0.50)", min_value=0.10, max_value=0.50, value=0.20, step=0.05)
    buff_base_rate = 60.0
    buff_fat_step = 0.50
    buff_snf_step = 0.30
else:
    st.sidebar.subheader("🦬 Buffalo Rate Parameters")
    buff_base_rate = st.sidebar.number_input("Buffalo Base Rate (for 6.0 FAT / 9.0 SNF)", min_value=1.0, max_value=200.0, value=60.0, step=0.5)
    buff_fat_step = st.sidebar.slider("Buffalo FAT Diff Rate per 0.1% (₹0.10 - ₹0.80)", min_value=0.10, max_value=0.80, value=0.50, step=0.05)
    buff_snf_step = st.sidebar.slider("Buffalo SNF Diff Rate per 0.1% (₹0.10 - ₹0.80)", min_value=0.10, max_value=0.80, value=0.30, step=0.05)
    cow_base_rate = 35.0
    cow_fat_step = 0.30
    cow_snf_step = 0.20

st.sidebar.markdown("---")
st.sidebar.header("📝 Daily Milk Entry")

farmer_name = st.sidebar.text_input("Farmer Name / Code")
shift = st.sidebar.selectbox("Shift", ["Morning", "Evening"])
selected_animal = st.sidebar.selectbox("Animal", ["Cow", "Buffalo"])
liters = st.sidebar.number_input("Liters", min_value=0.1, max_value=500.0, value=5.0, step=0.5)

# Input ranges based on animal
if selected_animal == "Cow":
    fat = st.sidebar.number_input("FAT % (Cow)", min_value=2.0, max_value=10.0, value=3.5, step=0.1)
    snf = st.sidebar.number_input("SNF % (Cow)", min_value=6.0, max_value=12.0, value=8.5, step=0.1)
else:
    fat = st.sidebar.number_input("FAT % (Buffalo)", min_value=3.0, max_value=15.0, value=6.0, step=0.1)
    snf = st.sidebar.number_input("SNF % (Buffalo)", min_value=6.0, max_value=12.0, value=9.0, step=0.1)

date_entry = st.sidebar.date_input("Date", datetime.today())

# --- RATE CALCULATION ENGINE ---
def calculate_standard_rate(animal, fat_val, snf_val):
    if animal == "Cow":
        base_fat, base_snf = 3.5, 8.5
        base_rate = cow_base_rate
        fat_diff_rate = cow_fat_step
        snf_diff_rate = cow_snf_step
    else:
        base_fat, base_snf = 6.0, 9.0
        base_rate = buff_base_rate
        fat_diff_rate = buff_fat_step
        snf_diff_rate = buff_snf_step

    # Calculate differences in steps of 0.1%
    fat_diff = round((fat_val - base_fat) * 10, 2)
    snf_diff = round((snf_val - base_snf) * 10, 2)

    final_rate = base_rate + (fat_diff * fat_diff_rate) + (snf_diff * snf_diff_rate)
    return max(0.0, round(final_rate, 2))

calculated_rate = calculate_standard_rate(selected_animal, fat, snf)
total_amount = round(calculated_rate * liters, 2)

st.sidebar.info(f"💡 **Rate/Liter:** ₹{calculated_rate}\n\n💰 **Total Amount:** ₹{total_amount}")

if st.sidebar.button("Save Entry"):
    if farmer_name.strip() != "":
        st.session_state.entries.append({
            "Date": date_entry.strftime("%Y-%m-%d"),
            "Farmer": farmer_name,
            "Shift": shift,
            "Animal": selected_animal,
            "Liters": liters,
            "FAT": fat,
            "SNF": snf,
            "Rate/L": calculated_rate,
            "Total Amount": total_amount
        })
        st.sidebar.success("Entry Saved Successfully!")
    else:
        st.sidebar.error("Please enter Farmer Name!")

# --- MAIN DASHBOARD ---
st.subheader("📋 Collection History")

if st.session_state.entries:
    df = pd.DataFrame(st.session_state.entries)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("💰 10-Day Payment Summary")
    
    summary = df.groupby("Farmer").agg(
        Total_Liters=("Liters", "sum"),
        Total_Payment=("Total Amount", "sum")
    ).reset_index()
    
    st.table(summary)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Excel/CSV Report", data=csv, file_name="milk_collection_report.csv", mime="text/csv")
else:
    st.info("No collection entries yet. Use the sidebar to add entries.")
