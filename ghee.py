import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🧈 Mercy Ghee Management System")

# Initialize data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "DateTime", "Person", "100ml", "200ml", "500ml", "1L"
    ])

# ---- ADD STOCK ----
st.header("➕ Add Stock")

col1, col2, col3, col4 = st.columns(4)

with col1:
    add_100 = st.number_input("100ml", min_value=0, step=1)
with col2:
    add_200 = st.number_input("200ml", min_value=0, step=1)
with col3:
    add_500 = st.number_input("500ml", min_value=0, step=1)
with col4:
    add_1l = st.number_input("1L", min_value=0, step=1)

if st.button("Add Stock"):
    new_row = pd.DataFrame([{
        "DateTime": datetime.now(),
        "Person": "Stock",
        "100ml": add_100,
        "200ml": add_200,
        "500ml": add_500,
        "1L": add_1l
    }])
    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
    st.success("Stock Added!")

# ---- SALE ----
st.header("🛒 Sale Entry")

person = st.text_input("Person Name")

col1, col2, col3, col4 = st.columns(4)

with col1:
    s_100 = st.number_input("Sell 100ml", min_value=0, step=1)
with col2:
    s_200 = st.number_input("Sell 200ml", min_value=0, step=1)
with col3:
    s_500 = st.number_input("Sell 500ml", min_value=0, step=1)
with col4:
    s_1l = st.number_input("Sell 1L", min_value=0, step=1)

if st.button("Add Sale"):
    new_row = pd.DataFrame([{
        "DateTime": datetime.now(),
        "Person": person,
        "100ml": -s_100,
        "200ml": -s_200,
        "500ml": -s_500,
        "1L": -s_1l
    }])
    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
    st.success("Sale Recorded!")

# ---- DISPLAY ----
st.header("📊 Records")
st.dataframe(st.session_state.data)

# ---- SUMMARY ----
st.header("📈 Summary")

total_100 = st.session_state.data["100ml"].sum()
total_200 = st.session_state.data["200ml"].sum()
total_500 = st.session_state.data["500ml"].sum()
total_1l = st.session_state.data["1L"].sum()

st.write(f"100ml Balance: {total_100}")
st.write(f"200ml Balance: {total_200}")
st.write(f"500ml Balance: {total_500}")
st.write(f"1L Balance: {total_1l}")