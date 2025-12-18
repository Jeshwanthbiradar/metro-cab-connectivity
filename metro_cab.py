import streamlit as st
import time
import qrcode
from io import BytesIO
import base64
import uuid

# ---------------- CONFIGURATION ----------------
st.set_page_config(page_title="Metro & Cab Booking", page_icon="🎫", layout="centered")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    /* --- RADIO BUTTONS AS BOXES --- */
    div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    div[role="radiogroup"] {
        gap: 15px;
    }
    div[role="radiogroup"] label {
        background-color: transparent;
        padding: 10px 25px;
        border-radius: 8px;
        border: 1px solid #ccc;
        cursor: pointer;
        transition: 0.2s;
        text-align: center;
        font-weight: 600;
    }
    div[role="radiogroup"] label:hover {
        border-color: #28a745;
        color: #28a745;
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
    }

    /* --- TICKET CARD STYLING --- */
    .ticket-card {
        background-color: #ffffff; 
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-top: 5px solid #28a745;
        margin-top: 20px;
        font-family: sans-serif;
    }
    
    .ticket-header {
        text-align: center;
        font-size: 22px;
        font-weight: 800;
        color: #28a745;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 20px;
        border-bottom: 2px dashed #eee;
        padding-bottom: 15px;
    }

    .ticket-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f9f9f9;
    }
    
    .ticket-label {
        font-size: 14px;
        color: #888;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .ticket-value {
        font-size: 16px;
        color: #333333 !important; 
        font-weight: 700;
        text-align: right;
    }

    .qr-holder {
        margin-top: 20px;
        text-align: center;
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px dashed #ccc;
    }
</style>
""", unsafe_allow_html=True) 

# ---------------- FUNCTIONS ----------------
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# ---------------- MAIN APP ----------------
st.title("🚇 Metro Smart Book")

with st.container(border=True):
    # Inputs
    name = st.text_input("Passenger Name", placeholder="e.g. John Doe")
    
    c1, c2 = st.columns(2)
    with c1:
        from_st = st.selectbox("From", ["Ameerpet", "Hitech City", "Jubilee Hills", "Kukatpally"])
    with c2:
        to_st = st.selectbox("To", ["Hitech City", "Ameerpet", "Jubilee Hills", "Kukatpally"])

    tickets = st.selectbox("Count", [1, 2, 3, 4, 5])
    
    st.markdown("---")
    
    # Cab Logic
    st.write("**Need a connecting Cab?**")
    cab_req = st.radio("Cab", ["Yes", "No"], horizontal=True, label_visibility="collapsed", index=1)
    
    drop_loc = ""
    if cab_req == "Yes":
        drop_loc = st.text_input("Drop Location", placeholder="Enter destination area...")

    st.write("") # Spacer

    # Book Button
    if st.button("Confirm Booking", type="primary", use_container_width=True):
        if not name:
            st.error("Please enter passenger name.")
        elif from_st == to_st:
            st.error("Source and Destination cannot be the same.")
        elif cab_req == "Yes" and not drop_loc:
            st.error("Please enter drop location.")
        else:
            with st.spinner("Generating Pass..."):
                time.sleep(1)
                
            # Logic variables
            tid = str(uuid.uuid4())[:8].upper()
            
            # 1. Prepare QR Data
            qr_payload = f"ID:{tid}|USER:{name}|TRIP:{from_st}>{to_st}"
            if cab_req == "Yes":
                qr_payload += f"|CAB:YES|DROP:{drop_loc}"
            else:
                qr_payload += "|CAB:NO"
                
            qr_img = generate_qr(qr_payload)

            # 2. Build Conditional HTML for Cab
            # If Yes: create the rows. If No: empty string.
            cab_html_block = ""
            if cab_req == "Yes":
                cab_html_block = f"""
<div class="ticket-row">
    <span class="ticket-label">Cab Status</span>
    <span class="ticket-value" style="color: #28a745">CONFIRMED</span>
</div>
<div class="ticket-row">
    <span class="ticket-label">pickup Location</span>
    <span class="ticket-value">{to_st}</span>
</div>
<div class="ticket-row">
    <span class="ticket-label">Drop Location</span>
    <span class="ticket-value">{drop_loc}</span>
</div>
"""

            # 3. Final HTML Assembly
            # We insert {cab_html_block} into the main string
            html_code = f"""
<div class="ticket-card">
<div class="ticket-header">BOARDING PASS</div>
<div class="ticket-row">
    <span class="ticket-label">Passenger</span>
    <span class="ticket-value">{name}</span>
</div>
<div class="ticket-row">
    <span class="ticket-label">Route</span>
    <span class="ticket-value">{from_st} ➝ {to_st}</span>
</div>
<div class="ticket-row">
    <span class="ticket-label">Tickets</span>
    <span class="ticket-value">{tickets}</span>
</div>
{cab_html_block}
<div class="qr-holder">
    <img src="data:image/png;base64,{qr_img}" width="150" style="border-radius:5px;">
    <br><small style="color:#888; font-family:monospace;">ID: {tid}</small>
</div>
</div>
"""
            
            
            st.markdown(html_code, unsafe_allow_html=True)
