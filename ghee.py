import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Mercy Ghee", layout="wide")

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
    add_100 = st.number_input("100ml", min_value=0, step=1, key="add100")
with col2:
    add_200 = st.number_input("200ml", min_value=0, step=1, key="add200")
with col3:
    add_500 = st.number_input("500ml", min_value=0, step=1, key="add500")
with col4:
    add_1l = st.number_input("1L", min_value=0, step=1, key="add1l")

if st.button("Add Stock"):
    new_row = pd.DataFrame([{
        "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Person": "Stock Added",
        "100ml": add_100,
        "200ml": add_200,
        "500ml": add_500,
        "1L": add_1l
    }])
    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
    st.success("✅ Stock Added!")

# ---- SALE ----
st.header("🛒 Sale Entry")

person = st.text_input("Person Name")

col1, col2, col3, col4 = st.columns(4)

with col1:
    s_100 = st.number_input("Sell 100ml", min_value=0, step=1, key="s100")
with col2:
    s_200 = st.number_input("Sell 200ml", min_value=0, step=1, key="s200")
with col3:
    s_500 = st.number_input("Sell 500ml", min_value=0, step=1, key="s500")
with col4:
    s_1l = st.number_input("Sell 1L", min_value=0, step=1, key="s1l")

if st.button("Add Sale"):
    if person == "":
        st.warning("⚠️ Enter person name")
    else:
        new_row = pd.DataFrame([{
            "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Person": person,
            "100ml": -s_100,
            "200ml": -s_200,
            "500ml": -s_500,
            "1L": -s_1l
        }])
        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.success("✅ Sale Recorded!")

# ---- DISPLAY ----
st.header("📊 Records")

if st.session_state.data.empty:
    st.info("No records yet")
else:
    st.dataframe(st.session_state.data, use_container_width=True)

# ---- SUMMARY ----
st.header("📈 Summary")

total_100 = st.session_state.data["100ml"].sum()
total_200 = st.session_state.data["200ml"].sum()
total_500 = st.session_state.data["500ml"].sum()
total_1l = st.session_state.data["1L"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("100ml Balance", total_100)
col2.metric("200ml Balance", total_200)
col3.metric("500ml Balance", total_500)
col4.metric("1L Balance", total_1l)
