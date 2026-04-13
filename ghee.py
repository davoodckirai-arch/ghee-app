# ======================
# DELIVERY + RETURN (NEW)
# ======================
st.header("📦 Delivery & Return")

d_name = st.text_input("Customer Name", key="d_name")

d1,d2,d3,d4,d5,d6 = st.columns(6)

# Taken (കൊണ്ടുപോയത്)
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
        # Return calculation
        r100 = t100 - sold100
        r200 = t200 - sold200
        r500 = t500 - sold500
        r1l  = t1l - sold1l
        r5l  = t5l - sold5l
        r16  = t16 - sold16

        # SALE ENTRY
        c.execute("""
        INSERT INTO ghee VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            selected_datetime,
            d_name,"","",
            -sold100,-sold200,-sold500,-sold1l,-sold5l,-sold16,
            d_cash,d_balance,
            st.session_state.user
        ))

        # RETURN ENTRY (unsold back to stock)
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
