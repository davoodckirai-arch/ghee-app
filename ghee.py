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

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# GHEE TABLE
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
    ml16_5l INTEGER,
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
# REGISTER
# ======================
def register():
    st.subheader("📝 Register")

    username = st.text_input("New Username", key="reg_user")
    password = st.text_input("New Password", type="password", key="reg_pass")

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

    username = st.text_input("Username", key="log_user")
    password = st.text_input("Password", type="password", key="log_pass")

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
# SESSION
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
# MAIN
# ======================
st.title("🧈 Mercy Ghee Management System")
st.sidebar.success(f"👤 {st.session_state.user}")

# ======================
# ADD STOCK
# ======================
st.header("➕ Add Stock")

c1, c2, c3, c4, c5, c6 = st.columns(6)

add_100 = c1.number_input("100ml", 0, key="a100")
add_200 = c2.number_input("200ml", 0, key="a200")
add_500 = c3.number_input("500ml", 0, key="a500")
add_1l  = c4.number_input("1L", 0, key="a1l")
add_5l  = c5.number_input("5L", 0, key="a5l")
add_16  = c6.number_input("16.5L", 0, key="a16")

if st.button("Add Stock"):
    c.execute("""
        INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Stock Added",
        add_100, add_200, add_500,
        add_1l, add_5l, add_16,
        st.session_state.user
    ))
    conn.commit()
    st.success("Stock Added")

# ======================
# SALE ENTRY
# ======================
st.header("🛒 Sale Entry")

person = st.text_input("Customer Name", key="cust")

s1, s2, s3, s4, s5, s6 = st.columns(6)

s_100 = s1.number_input("Sell 100ml", 0, key="s100")
s_200 = s2.number_input("Sell 200ml", 0, key="s200")
s_500 = s3.number_input("Sell 500ml", 0, key="s500")
s_1l  = s4.number_input("Sell 1L", 0, key="s1l")
s_5l  = s5.number_input("Sell 5L", 0, key="s5l")
s_16  = s6.number_input("Sell 16.5L", 0, key="s16")

if st.button("Add Sale"):
    if person == "":
        st.warning("Enter name")
    else:
        c.execute("""
            INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            person,
            -s_100, -s_200, -s_500,
            -s_1l, -s_5l, -s_16,
            st.session_state.user
        ))
        conn.commit()
        st.success("Sale Added")

# ======================
# RETURN ENTRY
# ======================
st.header("🔄 Return Entry")

r_person = st.text_input("Customer Name (Return)", key="rname")

r1, r2, r3, r4, r5, r6 = st.columns(6)

r_100 = r1.number_input("Return 100ml", 0, key="r100")
r_200 = r2.number_input("Return 200ml", 0, key="r200")
r_500 = r3.number_input("Return 500ml", 0, key="r500")
r_1l  = r4.number_input("Return 1L", 0, key="r1l")
r_5l  = r5.number_input("Return 5L", 0, key="r5l")
r_16  = r6.number_input("Return 16.5L", 0, key="r16")

if st.button("Add Return"):
    if r_person == "":
        st.warning("Enter customer name")
    else:
        c.execute("""
            INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"🔄 Return - {r_person}",
            r_100, r_200, r_500,
            r_1l, r_5l, r_16,
            st.session_state.user
        ))
        conn.commit()
        st.success("Return Added")

# ======================
# LOAD DATA
# ======================
df = pd.read_sql_query("SELECT * FROM ghee", conn)

# SAFE COLUMNS
for col in ["ml100","ml200","ml500","ml1l","ml5l","ml16_5l"]:
    if col not in df.columns:
        df[col] = 0

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
b5l  = df["ml5l"].sum()
b16  = df["ml16_5l"].sum()

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("100ml", b100)
c2.metric("200ml", b200)
c3.metric("500ml", b500)
c4.metric("1L", b1l)
c5.metric("5L", b5l)
c6.metric("16.5L", b16)

# ======================
# DOWNLOAD
# ======================
st.header("⬇️ Download")

if not df.empty:
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        "Download Excel",
        output.getvalue(),
        "ghee_data.xlsx"
    )

# ======================
# LOGOUT
# ======================
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
