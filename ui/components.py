import streamlit as st
from datetime import datetime

def render_analysis_results(category, recommended_authority, llm_response):
    st.markdown("---")
    st.subheader("📊 Legal Analysis & Strategy")
    st.success("✅ Analysis Complete!")
    
    cat_col, auth_col = st.columns([1.5, 3.5])
    with cat_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.success(f"📌 *Detected Category:* {category}")
        else:
            st.warning(f"⚠️ *Detected Category:* {category}")
    with auth_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.info(f"🏢 *Recommended Authority:* {recommended_authority}")
        
    st.markdown(llm_response)

def render_personalization_form(default_type, default_auth):
    st.markdown("---")
    st.subheader("📄 Auto-Draft Formal Document")
    st.markdown("Generate a meticulously formatted legal document ready for submission.")
    
    with st.expander("📝 Personalize Document (Optional)", expanded=True):
        st.markdown("Fill in the details below to automatically include them in your draft. Leave blank to keep placeholders.")
        
        c_type_col1, c_type_col2 = st.columns(2)
        with c_type_col1:
            custom_doc_type = st.text_input("Complaint Type", value=default_type, help="E.g., FIR, Consumer Complaint, College Application")
        with c_type_col2:
            custom_authority = st.text_input("Addressing Authority (To:)", value=default_auth, help="You can override the auto-filled authority here.")
            
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            p_name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
            p_age = st.text_input("Age", placeholder="e.g. 30")
            p_phone = st.text_input("Phone Number", placeholder="e.g. +91 9876543210")
            p_email = st.text_input("Email Address", placeholder="e.g. rahul@example.com")
        with f_col2:
            p_date = st.date_input("Date", value=datetime.today())
            p_address = st.text_area("Your Address", height=68, placeholder="e.g. 123, Main Street, Mumbai")
            p_location = st.text_input("Incident Location", placeholder="e.g. Mumbai, Maharashtra")
            p_police = st.text_input("Police Station Name", placeholder="e.g. Andheri Police Station")
            
    return custom_doc_type, custom_authority, {
        "p_name": p_name,
        "p_age": p_age,
        "p_phone": p_phone,
        "p_email": p_email,
        "p_date": p_date,
        "p_address": p_address,
        "p_location": p_location,
        "p_police": p_police
    }

def render_draft_review_tools():
    col_header, col_copy = st.columns([5, 1])
    with col_header:
        st.markdown("### Step 1: Review Your Complaint")
        st.caption("Review your draft below. Use the copy button in the top-right of the box.")
    with col_copy:
        st.write("") # Spacing alignment
        if st.button("📋 Copy Text", use_container_width=True):
            st.toast("Copied to clipboard ✅")
            
    st.code(st.session_state.complaint_draft, language="text", wrap_lines=True)
    st.markdown("<br>", unsafe_allow_html=True)

def render_email_sender_form():
    st.divider()
    st.markdown("### Step 2: Send Complaint via Email")
    st.caption("Enter authority email (police, principal, company, etc.)")
    
    recipient_email = st.text_input("Recipient Email Address", placeholder="e.g. support@company.com")
    subject = st.text_input("Email Subject", value="Official Legal Complaint Draft")
    
    st.markdown("<br>", unsafe_allow_html=True)
    send_email_clicked = st.button("🚀 Send Complaint via Email", type="primary", use_container_width=True)
    
    return recipient_email, subject, send_email_clicked
