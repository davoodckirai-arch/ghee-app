import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import io

st.set_page_config(page_title="Mercy Ghee", layout="wide")

# ======================
# DATABASE SETUP (USERS + DATA)
# ======================
conn = sqlite3.connect("ghee_app.db", check_same_thread=False)
c = conn.cursor()

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# GHEE DATA TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS ghee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT,
    person TEXT,
    ml100 INTEGER,
    ml200 INTEGER,
    ml500 INTEGER,
    ml1l INTEGER,
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
# REGISTER
# ======================
def register():
    st.subheader("📝 Register")

    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")

    if st.button("Register"):
        if username == "" or password == "":
            st.warning("Fill all fields")
        else:
            try:
                c.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hash_password(password))
                )
                conn.commit()
                st.success("Account created! Now login")
            except:
                st.error("Username already exists")

# ======================
# LOGIN
# ======================
def login():
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hash_password(password))
        )
        user = c.fetchone()

        if user:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Invalid credentials")

# ======================
# SESSION CHECK
# ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if menu == "Register":
        register()
    else:
        login()

    st.stop()

# ======================
# MAIN APP
# ======================
st.title("🧈 Mercy Ghee Management System")

st.sidebar.success(f"👤 Logged in: {st.session_state.user}")

# ======================
# ADD STOCK
# ======================
st.header("➕ Add Stock")

c1, c2, c3, c4 = st.columns(4)

add_100 = c1.number_input("100ml", min_value=0, step=1)
add_200 = c2.number_input("200ml", min_value=0, step=1)
add_500 = c3.number_input("500ml", min_value=0, step=1)
add_1l  = c4.number_input("1L", min_value=0, step=1)

if st.button("Add Stock"):
    c.execute("""
        INSERT INTO ghee (datetime, person, ml100, ml200, ml500, ml1l, user)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Stock Added",
        add_100,
        add_200,
        add_500,
        add_1l,
        st.session_state.user
    ))
    conn.commit()
    st.success("✅ Stock Added!")

# ======================
# SALE ENTRY
# ======================
st.header("🛒 Sale Entry")

person = st.text_input("Customer Name")

s1, s2, s3, s4 = st.columns(4)

s_100 = s1.number_input("Sell 100ml", min_value=0, step=1)
s_200 = s2.number_input("Sell 200ml", min_value=0, step=1)
s_500 = s3.number_input("Sell 500ml", min_value=0, step=1)
s_1l  = s4.number_input("Sell 1L", min_value=0, step=1)

if st.button("Add Sale"):
    if person.strip() == "":
        st.warning("⚠️ Enter customer name")
    else:
        c.execute("""
            INSERT INTO ghee (datetime, person, ml100, ml200, ml500, ml1l, user)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            person,
            -s_100,
            -s_200,
            -s_500,
            -s_1l,
            st.session_state.user
        ))
        conn.commit()
        st.success("✅ Sale Added!")

# ======================
# LOAD DATA
# ======================
df = pd.read_sql_query("SELECT * FROM ghee", conn)

# ======================
# RECORDS
# ======================
st.header("📊 Records")
st.dataframe(df, use_container_width=True)

# ======================
# BALANCE
# ======================
st.header("📈 Current Balance")

b100 = df["ml100"].sum()
b200 = df["ml200"].sum()
b500 = df["ml500"].sum()
b1l  = df["ml1l"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("100ml", b100)
c2.metric("200ml", b200)
c3.metric("500ml", b500)
c4.metric("1L", b1l)

# ======================
# DOWNLOAD EXCEL
# ======================
st.header("⬇️ Download Data")

if not df.empty:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="GheeData")

    st.download_button(
        "📥 Download Excel",
        output.getvalue(),
        "mercy_ghee_data.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ======================
# LOGOUT
# ======================
st.sidebar.markdown("---")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.user = ""
    st.rerun()
