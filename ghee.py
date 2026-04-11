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
    ml100 INTEGER,
    ml200 INTEGER,
    ml500 INTEGER,
    ml1l INTEGER,
    ml5l INTEGER,
    ml10l INTEGER,
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
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        if u and p:
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, hash_password(p)))
                conn.commit()
                st.success("Account created")
            except:
                st.error("Username exists")
        else:
            st.warning("Fill all")

def login():
    st.subheader("🔐 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
        if c.fetchone():
            st.session_state.logged_in = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Invalid login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    m = st.sidebar.selectbox("Menu", ["Login", "Register"])
    if m == "Register":
        register()
    else:
        login()
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

add = [
    c1.number_input("100ml",0),
    c2.number_input("200ml",0),
    c3.number_input("500ml",0),
    c4.number_input("1L",0),
    c5.number_input("5L",0),
    c6.number_input("10L",0)
]

if st.button("Add Stock"):
    c.execute("""
    INSERT INTO ghee (datetime, person, ml100, ml200, ml500, ml1l, ml5l, ml10l, user)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now(), "Stock", *add, st.session_state.user))
    conn.commit()
    st.success("Stock Added")

# ======================
# LOAD DATA
# ======================
df = pd.read_sql_query("SELECT * FROM ghee", conn)

# SAFE columns
for col in ["ml100","ml200","ml500","ml1l","ml5l","ml10l"]:
    if col not in df.columns:
        df[col] = 0

# ======================
# DATE FILTER
# ======================
st.header("📅 Filter")

if not df.empty:
    df["datetime"] = pd.to_datetime(df["datetime"])
    start = st.date_input("From", df["datetime"].min().date())
    end = st.date_input("To", df["datetime"].max().date())

    df = df[(df["datetime"].dt.date >= start) & (df["datetime"].dt.date <= end)]

# ======================
# BALANCE
# ======================
balance = {
    "ml100": df["ml100"].sum(),
    "ml200": df["ml200"].sum(),
    "ml500": df["ml500"].sum(),
    "ml1l": df["ml1l"].sum(),
    "ml5l": df["ml5l"].sum(),
    "ml10l": df["ml10l"].sum(),
}

st.header("📈 Current Balance")

cols = st.columns(6)
labels = ["100ml","200ml","500ml","1L","5L","10L"]

for i,key in enumerate(balance):
    cols[i].metric(labels[i], balance[key])

# ======================
# LOW STOCK WARNING
# ======================
st.header("⚠️ Low Stock Alert")

for k,v in balance.items():
    if v < 5:
        st.warning(f"{k} stock is low!")

# ======================
# SALE ENTRY (WITH CHECK)
# ======================
st.header("🛒 Sale")

name = st.text_input("Customer")

s1,s2,s3,s4,s5,s6 = st.columns(6)

sell = [
    s1.number_input("100ml",0),
    s2.number_input("200ml",0),
    s3.number_input("500ml",0),
    s4.number_input("1L",0),
    s5.number_input("5L",0),
    s6.number_input("10L",0)
]

if st.button("Add Sale"):
    if not name:
        st.warning("Enter name")
    else:
        # check stock
        ok = True
        keys = list(balance.keys())

        for i in range(6):
            if sell[i] > balance[keys[i]]:
                st.error(f"Not enough stock for {labels[i]}")
                ok = False
                break

        if ok:
            neg = [-x for x in sell]
            c.execute("""
            INSERT INTO ghee (datetime, person, ml100, ml200, ml500, ml1l, ml5l, ml10l, user)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now(), name, *neg, st.session_state.user))
            conn.commit()
            st.success("Sale Added")

# ======================
# TABLE
# ======================
st.header("📊 Records")
st.dataframe(df, use_container_width=True)

# ======================
# CHART
# ======================
st.header("📊 Sales Chart")

chart_df = df.copy()
chart_df = chart_df.groupby(chart_df["datetime"].dt.date).sum()

st.line_chart(chart_df[["ml100","ml200","ml500","ml1l","ml5l","ml10l"]])

# ======================
# DOWNLOAD
# ======================
st.header("⬇️ Download")

if not df.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button("Download Excel", output.getvalue(), "ghee.xlsx")

# ======================
# LOGOUT
# ======================
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
