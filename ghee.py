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
# HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# AUTH
# ======================
def register():
    st.subheader("📝 Register")
    u = st.text_input("Username", key="reg_u")
    p = st.text_input("Password", type="password", key="reg_p")

    if st.button("Register"):
        if u and p:
            try:
                c.execute("INSERT INTO users VALUES (NULL,?,?)",(u,hash_password(p)))
                conn.commit()
                st.success("Account created")
            except:
                st.error("Username exists")

def login():
    st.subheader("🔐 Login")
    u = st.text_input("Username", key="log_u")
    p = st.text_input("Password", type="password", key="log_p")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,hash_password(p)))
        if c.fetchone():
            st.session_state.logged_in=True
            st.session_state.user=u
            st.rerun()
        else:
            st.error("Invalid login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if not st.session_state.logged_in:
    m = st.sidebar.selectbox("Menu",["Login","Register"])
    if m=="Register": register()
    else: login()
    st.stop()

# ======================
# MAIN
# ======================
st.title("🧈 Mercy Ghee Management System")
st.sidebar.success(f"👤 {st.session_state.user}")

# ======================
# DATE
# ======================
selected_date = st.sidebar.date_input("Date")
selected_time = st.sidebar.time_input("Time")
selected_datetime = datetime.combine(selected_date, selected_time)

# ======================
# ADD STOCK
# ======================
st.header("➕ Add Stock")

c1,c2,c3,c4,c5,c6 = st.columns(6)

a100 = c1.number_input("100ml",0,key="a100")
a200 = c2.number_input("200ml",0,key="a200")
a500 = c3.number_input("500ml",0,key="a500")
a1l  = c4.number_input("1L",0,key="a1l")
a5l  = c5.number_input("5L",0,key="a5l")
a16  = c6.number_input("16.5L",0,key="a16")

if st.button("Add Stock"):
    c.execute("""
    INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        selected_datetime,"Stock","","",
        a100,a200,a500,a1l,a5l,a16,
        0,0,
        st.session_state.user
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

cash = st.number_input("Cash Received",0.0,key="s_cash")
balance_amt = st.number_input("Balance (Credit)",0.0,key="s_bal")

s1,s2,s3,s4,s5,s6 = st.columns(6)

s100 = s1.number_input("100ml",0,key="s100")
s200 = s2.number_input("200ml",0,key="s200")
s500 = s3.number_input("500ml",0,key="s500")
s1l  = s4.number_input("1L",0,key="s1l")
s5l  = s5.number_input("5L",0,key="s5l")
s16  = s6.number_input("16.5L",0,key="s16")

if st.button("Add Sale"):
    if not name:
        st.warning("Enter name")
    else:
        c.execute("""
        INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            selected_datetime,
            name,phone,place,
            -s100,-s200,-s500,-s1l,-s5l,-s16,
            cash,balance_amt,
            st.session_state.user
        ))
        conn.commit()
        st.success("Sale Added")

# ======================
# DELIVERY + RETURN
# ======================
st.header("📦 Delivery & Return")

d_name = st.text_input("Customer Name", key="d_name")

d1,d2,d3,d4,d5,d6 = st.columns(6)

t100 = d1.number_input("Taken 100ml",0,key="t100")
t200 = d2.number_input("Taken 200ml",0,key="t200")
t500 = d3.number_input("Taken 500ml",0,key="t500")
t1l  = d4.number_input("Taken 1L",0,key="t1l")
t5l  = d5.number_input("Taken 5L",0,key="t5l")
t16  = d6.number_input("Taken 16.5L",0,key="t16")

st.subheader("Sold Quantity")

s1,s2,s3,s4,s5,s6 = st.columns(6)

sold100 = s1.number_input("Sold 100ml",0,key="ds100")
sold200 = s2.number_input("Sold 200ml",0,key="ds200")
sold500 = s3.number_input("Sold 500ml",0,key="ds500")
sold1l  = s4.number_input("Sold 1L",0,key="ds1l")
sold5l  = s5.number_input("Sold 5L",0,key="ds5l")
sold16  = s6.number_input("Sold 16.5L",0,key="ds16")

d_cash = st.number_input("Cash Received",0.0,key="d_cash")
d_balance = st.number_input("Balance",0.0,key="d_bal")

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
        INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            selected_datetime,
            d_name,"","",
            -sold100,-sold200,-sold500,-sold1l,-sold5l,-sold16,
            d_cash,d_balance,
            st.session_state.user
        ))

        # RETURN
        c.execute("""
        INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            selected_datetime,
            "Return","","",
            r100,r200,r500,r1l,r5l,r16,
            0,0,
            st.session_state.user
        ))

        conn.commit()
        st.success("Delivery + Return Added ✅")

# ======================
# BALANCE COLLECTION
# ======================
st.header("💳 Balance Collection")

collected = st.number_input("Collected Amount",0.0)

if st.button("Add Collection"):
    c.execute("""
    INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        selected_datetime,
        "Balance Paid","","",
        0,0,0,0,0,0,
        collected,-collected,
        st.session_state.user
    ))
    conn.commit()
    st.success("Balance Updated")

# ======================
# DELETE
# ======================
st.header("🗑️ Delete Record")

df = pd.read_sql_query("SELECT * FROM ghee", conn)

if not df.empty:
    record_id = st.selectbox("Select Record ID", df["id"])
    
    if st.button("Delete"):
        c.execute("DELETE FROM ghee WHERE id=?", (record_id,))
        conn.commit()
        st.success("Deleted Successfully")
        st.rerun()

# ======================
# DATA
# ======================
st.header("📊 Records")
df = pd.read_sql_query("SELECT * FROM ghee", conn)
st.dataframe(df, use_container_width=True)

# ======================
# STOCK
# ======================
st.header("📈 Stock Balance")

cols = ["ml100","ml200","ml500","ml1l","ml5l","ml16_5l"]
labels = ["100ml","200ml","500ml","1L","5L","16.5L"]

c1,c2,c3,c4,c5,c6 = st.columns(6)

for i in range(6):
    [c1,c2,c3,c4,c5,c6][i].metric(labels[i], df[cols[i]].sum())

# ======================
# MANUAL ADJUST
# ======================
st.header("⚙️ Manual Adjustment (Display Only)")

adj_cash = st.number_input("Adjust Cash (+ / -)", 0.0)
adj_balance = st.number_input("Adjust Balance (+ / -)", 0.0)

# ======================
# CASH
# ======================
st.header("💰 Cash Summary")

total_cash = df["cash"].sum() + adj_cash
total_balance = df["balance"].sum() + adj_balance

st.metric("Total Cash", total_cash)
st.metric("Total Balance", total_balance)

# ======================
# DOWNLOAD
# ======================
st.header("⬇️ Download")

output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)

st.download_button("Download Excel", output.getvalue(), "ghee.xlsx")

# ======================
# LOGOUT
# ======================
if st.sidebar.button("Logout"):
    st.session_state.logged_in=False
    st.rerun()
