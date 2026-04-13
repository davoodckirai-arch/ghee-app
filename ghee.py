import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import hashlib
import io

st.set_page_config(page_title="Mercy Ghee", layout="wide")

# ======================
# MYSQL CONNECTION (RAILWAY SAFE)
# ======================
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"],
        database=st.secrets["DB_NAME"]
    )

conn = get_connection()
c = conn.cursor()

# ======================
# TABLES
# ======================
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS ghee (
    id INT AUTO_INCREMENT PRIMARY KEY,
    datetime TEXT,
    person TEXT,
    phone TEXT,
    place TEXT,
    ml100 INT,
    ml200 INT,
    ml500 INT,
    ml1l INT,
    ml5l INT,
    ml16_5l INT,
    cash FLOAT,
    balance FLOAT,
    user TEXT
)
""")

conn.commit()

# ======================
# HASH
# ======================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ======================
# SESSION
# ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ======================
# LOGIN
# ======================
def login():
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                  (u, hash_password(p)))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Invalid Login")

# ======================
# REGISTER
# ======================
def register():
    st.subheader("📝 Register")
    u = st.text_input("Username", key="r1")
    p = st.text_input("Password", type="password", key="r2")

    if st.button("Register"):
        try:
            c.execute("INSERT INTO users VALUES (NULL,%s,%s)",
                      (u, hash_password(p)))
            conn.commit()
            st.success("Account Created")
        except:
            st.error("Username Exists")

# ======================
# AUTH
# ======================
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
    if menu == "Login":
        login()
    else:
        register()
    st.stop()

st.title("🧈 Mercy Ghee System")
st.sidebar.success(f"👤 {st.session_state.user}")

# ======================
# DATE
# ======================
date = st.sidebar.date_input("Date")
time = st.sidebar.time_input("Time")
dt = datetime.combine(date, time)

# ======================
# ADD STOCK
# ======================
st.header("➕ Add Stock")

c1,c2,c3,c4,c5,c6 = st.columns(6)

a100 = c1.number_input("100ml",0)
a200 = c2.number_input("200ml",0)
a500 = c3.number_input("500ml",0)
a1l  = c4.number_input("1L",0)
a5l  = c5.number_input("5L",0)
a16  = c6.number_input("16.5L",0)

if st.button("Add Stock"):
    c.execute("""
    INSERT INTO ghee VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        str(dt),"Stock","","",
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

name = st.text_input("Customer Name")
phone = st.text_input("Phone")
place = st.text_input("Place")

cash = st.number_input("Cash",0.0)
balance = st.number_input("Balance",0.0)

s1,s2,s3,s4,s5,s6 = st.columns(6)

s100 = s1.number_input("100ml",0)
s200 = s2.number_input("200ml",0)
s500 = s3.number_input("500ml",0)
s1l  = s4.number_input("1L",0)
s5l  = s5.number_input("5L",0)
s16  = s6.number_input("16.5L",0)

if st.button("Add Sale"):
    if name:
        c.execute("""
        INSERT INTO ghee VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            str(dt),
            name,phone,place,
            -s100,-s200,-s500,-s1l,-s5l,-s16,
            cash,balance,
            st.session_state.user
        ))
        conn.commit()
        st.success("Sale Added")

# ======================
# DATA
# ======================
st.header("📊 Records")

c.execute("SELECT * FROM ghee")
rows = c.fetchall()

df = pd.DataFrame(rows, columns=[
    "id","datetime","person","phone","place",
    "ml100","ml200","ml500","ml1l","ml5l","ml16_5l",
    "cash","balance","user"
])

st.dataframe(df, use_container_width=True)

# ======================
# STOCK + CASH
# ======================
st.header("📈 Stock Balance")
for col in ["ml100","ml200","ml500","ml1l","ml5l","ml16_5l"]:
    st.metric(col, df[col].sum())

st.header("💰 Cash Summary")
st.metric("Total Cash", df["cash"].sum())
st.metric("Total Balance", df["balance"].sum())

# ======================
# DOWNLOAD
# ======================
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)

st.download_button("⬇ Download Excel", output.getvalue(), "ghee.xlsx")

# ======================
# LOGOUT
# ======================
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()