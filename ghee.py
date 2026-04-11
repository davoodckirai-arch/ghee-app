import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Mercy Ghee", layout="wide")

st.title("🧈 Mercy Ghee Management System")

# ======================
# SESSION DATA INIT
# ======================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["DateTime", "Person", "100ml", "200ml", "500ml", "1L"]
    )

# ======================
# ➕ ADD STOCK
# ======================
st.header("➕ Add Stock")

c1, c2, c3, c4 = st.columns(4)

add_100 = c1.number_input("100ml", min_value=0, step=1, key="a100")
add_200 = c2.number_input("200ml", min_value=0, step=1, key="a200")
add_500 = c3.number_input("500ml", min_value=0, step=1, key="a500")
add_1l  = c4.number_input("1L", min_value=0, step=1, key="a1l")

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

# ======================
# 🛒 SALE ENTRY
# ======================
st.header("🛒 Sale Entry")

person = st.text_input("Customer Name")

c1, c2, c3, c4 = st.columns(4)

s_100 = c1.number_input("Sell 100ml", min_value=0, step=1, key="s100")
s_200 = c2.number_input("Sell 200ml", min_value=0, step=1, key="s200")
s_500 = c3.number_input("Sell 500ml", min_value=0, step=1, key="s500")
s_1l  = c4.number_input("Sell 1L", min_value=0, step=1, key="s1l")

if st.button("Add Sale"):
    if person.strip() == "":
        st.warning("⚠️ Please enter customer name")
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

# ======================
# 📊 RECORDS
# ======================
st.header("📊 Records")

st.dataframe(st.session_state.data, use_container_width=True)

# ======================
# 📈 SUMMARY
# ======================
st.header("📈 Current Balance")

balance_100 = st.session_state.data["100ml"].sum()
balance_200 = st.session_state.data["200ml"].sum()
balance_500 = st.session_state.data["500ml"].sum()
balance_1l  = st.session_state.data["1L"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("100ml", balance_100)
c2.metric("200ml", balance_200)
c3.metric("500ml", balance_500)
c4.metric("1L", balance_1l)

# ======================
# 📥 DOWNLOAD EXCEL
# ======================
st.header("⬇️ Download Data")

if not st.session_state.data.empty:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.data.to_excel(writer, index=False, sheet_name="GheeData")

    excel_data = output.getvalue()

    st.download_button(
        label="📥 Download Excel File",
        data=excel_data,
        file_name="mercy_ghee_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("No data available to download")
