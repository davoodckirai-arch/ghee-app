import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import io

st.set_page_config(page_title="Mercy Ghee", layout="wide")

# ======================
# DATABASE
# ======================
conn = sqlite3.connect("ghee_app.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS ghee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT,
    person TEXT,
    phone TEXT,
    place TEXT,
    ml100 INTEGER,
    ml200 INTEGER,
    ml500 INTEGER,
    ml1l INTEGER,
    ml5l INTEGER,
    ml16_5l INTEGER,
    cash REAL,
    balance REAL,
    user TEXT
)
""")

conn.commit()

# ======================
# PASSWORD HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# SESSION INIT
# ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ======================
# REGISTER
# ======================
def register():
    st.subheader("📝 Register")
    u = st.text_input("Username", key="reg_u")
    p = st.text_input("Password", type="password", key="reg_p")

    if st.button("Register"):
        if u and p:
            try:
                c.execute(
                    "INSERT INTO users (username, password) VALUES (?,?)",
                    (u, hash_password(p))
                )
                conn.commit()
                st.success("Account created")
            except:
                st.error("Username already exists")

# ======================
# LOGIN
# ======================
def login():
    st.subheader("🔐 Login")
    u = st.text_input("Username", key="log_u")
    p = st.text_input("Password", type="password", key="log_p")

    if st.button("Login"):
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, hash_password(p))
        )
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Invalid login")

# ======================
# AUTH SYSTEM
# ======================
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
    if menu == "Register":
        register()
    else:
        login()
    st.stop()

# ======================
# MAIN UI
# ======================
st.title("🧈 Mercy Ghee Management System")
st.sidebar.success(f"👤 {st.session_state.user}")

# ======================
# DATE TIME
# ======================
selected_date = st.sidebar.date_input("Date")
selected_time = st.sidebar.time_input("Time")
selected_datetime = datetime.combine(selected_date, selected_time)

# ======================
# ADD STOCK
# ======================
st.header("➕ Add Stock")

c1,c2,c3,c4,c5,c6 = st.columns(6)

a100 = c1.number_input("100ml", 0, key="a100")
a200 = c2.number_input("200ml", 0, key="a200")
a500 = c3.number_input("500ml", 0, key="a500")
a1l  = c4.number_input("1L", 0, key="a1l")
a5l  = c5.number_input("5L", 0, key="a5l")
a16  = c6.number_input("16.5L", 0, key="a16")

if st.button("Add Stock"):
    c.execute("""
        INSERT INTO ghee (
            datetime, person, phone, place,
            ml100, ml200, ml500, ml1l, ml5l, ml16_5l,
            cash, balance, user
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        selected_datetime, "Stock", "", "",
        a100, a200, a500, a1l, a5l, a16,
        0, 0, st.session_state.user
    ))
    conn.commit()
    st.success("Stock Added")

# ======================
# SALE
# ======================
st.header("🛒 Sale Entry")

name = st.text_input("Customer Name", key="s_name")
phone = st.text_input("Phone", key="s_phone")
place = st.text_input("Place", key="s_place")

cash = st.number_input("Cash Received", 0.0, key="s_cash")
balance_amt = st.number_input("Balance", 0.0, key="s_bal")

s1,s2,s3,s4,s5,s6 = st.columns(6)

s100 = s1.number_input("100ml", 0, key="s100")
s200 = s2.number_input("200ml", 0, key="s200")
s500 = s3.number_input("500ml", 0, key="s500")
s1l  = s4.number_input("1L", 0, key="s1l")
s5l  = s5.number_input("5L", 0, key="s5l")
s16  = s6.number_input("16.5L", 0, key="s16")

if st.button("Add Sale"):
    if not name:
        st.warning("Enter customer name")
    else:
        c.execute("""
            INSERT INTO ghee (
                datetime, person, phone, place,
                ml100, ml200, ml500, ml1l, ml5l, ml16_5l,
                cash, balance, user
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            selected_datetime, name, phone, place,
            -s100, -s200, -s500, -s1l, -s5l, -s16,
            cash, balance_amt, st.session_state.user
        ))
        conn.commit()
        st.success("Sale Added")

# ======================
# DELIVERY & RETURN
# ======================
st.header("📦 Delivery & Return")

d_name = st.text_input("Customer Name (Delivery)", key="d_name")

d1,d2,d3,d4,d5,d6 = st.columns(6)

t100 = d1.number_input("Taken 100ml", 0, key="t100")
t200 = d2.number_input("Taken 200ml", 0, key="t200")
t500 = d3.number_input("Taken 500ml", 0, key="t500")
t1l  = d4.number_input("Taken 1L", 0, key="t1l")
t5l  = d5.number_input("Taken 5L", 0, key="t5l")
t16  = d6.number_input("Taken 16.5L", 0, key="t16")

st.subheader("Sold Quantity")

s1,s2,s3,s4,s5,s6 = st.columns(6)

sold100 = s1.number_input("Sold 100ml", 0, key="ds100")
sold200 = s2.number_input("Sold 200ml", 0, key="ds200")
sold500 = s3.number_input("Sold 500ml", 0, key="ds500")
sold1l  = s4.number_input("Sold 1L", 0, key="ds1l")
sold5l  = s5.number_input("Sold 5L", 0, key="ds5l")
sold16  = s6.number_input("Sold 16.5L", 0, key="ds16")

d_cash = st.number_input("Cash Received", 0.0, key="d_cash")
d_bal  = st.number_input("Balance", 0.0, key="d_bal")

if st.button("Submit Delivery"):
    if not d_name:
        st.warning("Enter name")
    else:
        r100 = t100 - sold100
        r200 = t200 - sold200
        r500 = t500 - sold500
        r1l  = t1l - sold1l
        r5l  = t5l - sold5l
        r16  = t16 - sold16

        # SALE
        c.execute("""
            INSERT INTO ghee (
                datetime, person, phone, place,
                ml100, ml200, ml500, ml1l, ml5l, ml16_5l,
                cash, balance, user
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            selected_datetime, d_name, "", "",
            -sold100, -sold200, -sold500, -sold1l, -sold5l, -sold16,
            d_cash, d_bal, st.session_state.user
        ))

        # RETURN
        c.execute("""
            INSERT INTO ghee (
                datetime, person, phone, place,
                ml100, ml200, ml500, ml1l, ml5l, ml16_5l,
                cash, balance, user
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            selected_datetime, "Return", "", "",
            r100, r200, r500, r1l, r5l, r16,
            0, 0, st.session_state.user
        ))

        conn.commit()
        st.success("Delivery + Return Added")

# ======================
# BALANCE COLLECTION
# ======================
st.header("💳 Balance Collection")

collected = st.number_input("Collected Amount", 0.0)

if st.button("Add Collection"):
    c.execute("""
        INSERT INTO ghee (
            datetime, person, phone, place,
            ml100, ml200, ml500, ml1l, ml5l, ml16_5l,
            cash, balance, user
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        selected_datetime, "Balance Paid", "", "",
        0,0,0,0,0,0,
        collected, -collected,
        st.session_state.user
    ))
    conn.commit()
    st.success("Balance Updated")

# ======================
# DATA
# ======================
st.header("📊 Records")

df = pd.read_sql_query("SELECT * FROM ghee", conn)
st.dataframe(df, use_container_width=True)

# ======================
# STOCK SUMMARY
# ======================
st.header("📈 Stock Balance")

if not df.empty:
    cols = ["ml100","ml200","ml500","ml1l","ml5l","ml16_5l"]
    labels = ["100ml","200ml","500ml","1L","5L","16.5L"]

    ccols = st.columns(6)

    for i in range(6):
        ccols[i].metric(labels[i], df[cols[i]].sum())

# ======================
# CASH SUMMARY
# ======================
st.header("💰 Cash Summary")

adj_cash = st.number_input("Adjust Cash (+/-)", 0.0)
adj_balance = st.number_input("Adjust Balance (+/-)", 0.0)

total_cash = df["cash"].sum() + adj_cash
total_balance = df["balance"].sum() + adj_balance

st.metric("Total Cash", total_cash)
st.metric("Total Balance", total_balance)

# ======================
# DOWNLOAD EXCEL (FIXED)
# ======================
st.header("⬇️ Download Excel")

output = io.BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)

output.seek(0)

st.download_button(
    "Download Excel",
    data=output,
    file_name="ghee.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ======================
# DELETE
# ======================
st.header("🗑️ Delete Record")

if not df.empty:
    record_id = st.selectbox("Select ID", df["id"])

    if st.button("Delete"):
        c.execute("DELETE FROM ghee WHERE id=?", (record_id,))
        conn.commit()
        st.success("Deleted")
        st.rerun()

# ======================
# LOGOUT
# ======================
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
