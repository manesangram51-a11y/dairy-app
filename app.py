import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dairy Farmer Collection & Billing", layout="wide"
)
st.title("🥛 Dairy Milk Collection & Billing System")

# Data storage (In-memory / Database mock)
if "collection_data" not in st.session_state:
  st.session_state.collection_data = []


# Rate Calculation Logic
def calculate_rate(animal, fat, snf):
  if animal == "Cow":
    # Cow Ranges: FAT 2.5 - 5.2 | SNF 8.0 - 9.0
    if 2.5 <= fat <= 5.2 and 8.0 <= snf <= 9.0:
      rate = (fat * 6.5) + (snf * 4.0)  # Standard Rate Matrix
      return round(rate, 2)
    else:
      return round((fat * 6.0) + (snf * 3.5), 2)  # Default/Out of range

  elif animal == "Buffalo":
    # Buffalo Ranges: FAT 5.5 - 11.0 | SNF 9.0 - 9.5
    if 5.5 <= fat <= 11.0 and 9.0 <= snf <= 9.5:
      rate = (fat * 7.5) + (snf * 4.5)
      return round(rate, 2)
    else:
      return round((fat * 7.0) + (snf * 4.0), 2)


# Payment Cycle Logic (10 Days Period)
def get_payment_cycle(date_obj):
  day = date_obj.day
  year = date_obj.year
  month = date_obj.strftime("%B")

  if 1 <= day <= 10:
    return f"Period 1 (1 to 10 {month} {year})"
  elif 11 <= day <= 20:
    return f"Period 2 (11 to 20 {month} {year})"
  else:
    return f"Period 3 (21 to End {month} {year})"


# --- SIDEBAR: ENTRY FORM ---
st.sidebar.header("📥 Daily Collection Entry")

farmer_id = st.sidebar.text_input("Farmer ID / Name", "Kisan 1")
entry_date = st.sidebar.date_input("Date", datetime.date.today())
shift = st.sidebar.selectbox("Shift", ["Morning", "Evening"])
animal = st.sidebar.selectbox("Animal Type", ["Cow", "Buffalo"])

quantity = st.sidebar.number_input(
    "Quantity (Liters)", min_value=0.1, value=10.0, step=0.5
)

if animal == "Cow":
  fat = st.sidebar.slider(
      "FAT (%)", min_value=2.5, max_value=5.2, value=3.5, step=0.1
  )
  snf = st.sidebar.slider(
      "SNF (%)", min_value=8.0, max_value=9.0, value=8.5, step=0.1
  )
else:
  fat = st.sidebar.slider(
      "FAT (%)", min_value=5.5, max_value=11.0, value=6.5, step=0.1
  )
  snf = st.sidebar.slider(
      "SNF (%)", min_value=9.0, max_value=9.5, value=9.0, step=0.1
  )

calculated_rate = calculate_rate(animal, fat, snf)
total_amount = round(quantity * calculated_rate, 2)
cycle = get_payment_cycle(entry_date)

st.sidebar.info(f"**Calculated Rate:** ₹{calculated_rate} / Liter")
st.sidebar.success(f"**Total Amount:** ₹{total_amount}")

if st.sidebar.button("Save Entry"):
  entry = {
      "Date": entry_date,
      "Farmer": farmer_id,
      "Shift": shift,
      "Animal": animal,
      "Qty (L)": quantity,
      "FAT": fat,
      "SNF": snf,
      "Rate/L": calculated_rate,
      "Total (₹)": total_amount,
      "Billing Cycle": cycle,
  }
  st.session_state.collection_data.append(entry)
  st.sidebar.success("Entry Saved Successfully!")

# --- MAIN DASHBOARD & REPORTS ---
col1, col2 = st.columns(2)

with col1:
  st.subheader("📋 Collection History")
  if st.session_state.collection_data:
    df = pd.DataFrame(st.session_state.collection_data)
    st.dataframe(df, use_container_width=True)
  else:
    st.write("No collection entries yet.")

with col2:
  st.subheader("💰 10-Day Payment Summary")
  if st.session_state.collection_data:
    df = pd.DataFrame(st.session_state.collection_data)
    summary = (
        df.groupby(["Farmer", "Billing Cycle"])[["Qty (L)", "Total (₹)"]]
        .sum()
        .reset_index()
    )
    st.dataframe(summary, use_container_width=True)
  else:
    st.write("Summary will appear here.")
