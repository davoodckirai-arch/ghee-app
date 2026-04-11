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
        datetime.now(),"Stock","","",
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
            datetime.now(),
            name,phone,place,
            -s100,-s200,-s500,-s1l,-s5l,-s16,
            cash,balance_amt,
            st.session_state.user
        ))
        conn.commit()
        st.success("Sale Added")

# ======================
# RETURN
# ======================
st.header("🔄 Return Entry")

r_name = st.text_input("Customer Name (Return)", key="r_name")
r_cash = st.number_input("Cash Returned",0.0,key="r_cash")
r_balance = st.number_input("Balance Adjust",0.0,key="r_bal")

r1,r2,r3,r4,r5,r6 = st.columns(6)

r100 = r1.number_input("100ml",0,key="r100")
r200 = r2.number_input("200ml",0,key="r200")
r500 = r3.number_input("500ml",0,key="r500")
r1l  = r4.number_input("1L",0,key="r1l")
r5l  = r5.number_input("5L",0,key="r5l")
r16  = r6.number_input("16.5L",0,key="r16")

if st.button("Add Return"):
    if not r_name:
        st.warning("Enter name")
    else:
        c.execute("""
        INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            datetime.now(),
            f"🔄 Return - {r_name}","","",
            r100,r200,r500,r1l,r5l,r16,
            -r_cash,-r_balance,
            st.session_state.user
        ))
        conn.commit()
        st.success("Return Added")

# ======================
# DATA
# ======================
df = pd.read_sql_query("SELECT * FROM ghee", conn)

st.header("📊 Records")
st.dataframe(df, use_container_width=True)

# ======================
# BALANCE
# ======================
st.header("📈 Stock Balance")

cols = ["ml100","ml200","ml500","ml1l","ml5l","ml16_5l"]
labels = ["100ml","200ml","500ml","1L","5L","16.5L"]

c1,c2,c3,c4,c5,c6 = st.columns(6)

for i in range(6):
    [c1,c2,c3,c4,c5,c6][i].metric(labels[i], df[cols[i]].sum())

# ======================
# CASH SUMMARY
# ======================
st.header("💰 Cash Summary")

st.metric("Total Cash", df["cash"].sum())
st.metric("Total Balance", df["balance"].sum())

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
