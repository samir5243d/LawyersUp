import streamlit as st

# Configure page initially
st.set_page_config(page_title="Lawyer's Up - AI Legal Assistant", page_icon="⚖️", layout="wide")

from config.settings import ALL_CATEGORIES, EMAIL_USER, EMAIL_PASS
from utils.helpers import get_authority_for_category, get_doc_type_for_category, get_tone_for_category
from services.ai_service import analyze_legal_issue, generate_complaint_draft
from services.pdf_service import generate_pdf
from services.email_service import send_email
from ui.layout import render_sidebar, render_footer
from ui.components import render_analysis_results, render_personalization_form, render_draft_review_tools, render_email_sender_form

# ═══════════════════════════════════════════════════════════════
# MAIN UI FLOW
# ═══════════════════════════════════════════════════════════════

selected_language = render_sidebar()

st.title("🏛️ Lawyer's Up : Legal AI Assistant")
st.markdown("Describe your issue below to instantly receive professional legal guidance. 🚀")

cat_col1, cat_col2 = st.columns([1.5, 3.5])
with cat_col1:
    manual_category = st.selectbox(
        "📂 Select Complaint Category",
        ["Auto-Detect"] + ALL_CATEGORIES,
        help="Choose a category or let AI auto-detect from your description."
    )
with cat_col2:
    if manual_category != "Auto-Detect":
        auto_authority = get_authority_for_category(manual_category)
        st.text_input("🏢 Recommended Authority (auto-filled)", value=auto_authority, disabled=True, help="This authority is auto-filled based on your selected category.")
    else:
        st.text_input("🏢 Recommended Authority", value="Will be detected from your description", disabled=True, help="Select a category or let AI determine the appropriate authority.")

user_input = st.text_area("✍️ *Enter your problem:*", height=150, placeholder="E.g., I was defrauded of money online by a fake e-commerce website...")

col1, col2 = st.columns([1, 4])
with col1:
    get_help_btn = st.button("✨ Get Legal Help", use_container_width=True)

# Processing the Request
if get_help_btn:
    if not user_input.strip():
        st.warning("Please enter your problem before submitting.")
    else:
        with st.spinner("Analyzing your issue..."):
            result = analyze_legal_issue(user_input, manual_category, ALL_CATEGORIES, selected_language)
            
            if result.get("success"):
                st.session_state.category = result["category"]
                st.session_state.recommended_authority = result["recommended_authority"]
                st.session_state.llm_response = result["llm_response"]
                st.session_state.user_problem = user_input
                st.session_state.language = selected_language
                st.session_state.complaint_draft = None  # Reset previous drafts
            else:
                st.error(result.get("error"))
                if "details" in result:
                    st.write("Response details:", result["details"])

# Displaying Analysis Results
if "llm_response" in st.session_state and st.session_state.llm_response:
    render_analysis_results(st.session_state.category, st.session_state.get("recommended_authority", ""), st.session_state.llm_response)
    
    category = st.session_state.category
    if category not in ["Not a Legal Issue", "Unknown Category"]:
        default_type = get_doc_type_for_category(category)
        default_auth = st.session_state.get("recommended_authority", get_authority_for_category(category))
        default_tone = get_tone_for_category(category)
        
        custom_doc_type, custom_authority, p_details = render_personalization_form(default_type, default_auth)
        
        btn_col, empty_col2 = st.columns([1.5, 3.5])
        with btn_col:
            gen_btn = st.button("🖋️ Generate Draft", use_container_width=True)
            
        if gen_btn:
            with st.spinner(f"Drafting your {category} document..."):
                draft_res = generate_complaint_draft(category, custom_authority, custom_doc_type, default_tone, p_details, st.session_state.user_problem, st.session_state.language)
                if draft_res.get("success"):
                    st.session_state.complaint_draft = draft_res["draft"]
                else:
                    st.error(draft_res.get("error"))
                    
        if st.session_state.get("complaint_draft"):
            st.success("✨ Draft generated successfully!")
            
            render_draft_review_tools()
            
            pdf_buffer = generate_pdf(st.session_state.complaint_draft)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_buffer,
                file_name="legal_complaint_draft.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            recipient_email, subject, send_email_clicked = render_email_sender_form()
            
            if send_email_clicked:
                if not EMAIL_USER or not EMAIL_PASS:
                    st.error("Sender credentials (EMAIL_USER, EMAIL_PASS) not found in .env file. Please configure them.")
                elif not recipient_email.strip():
                    st.warning("Please provide a recipient email address.")
                else:
                    with st.spinner("Sending email..."):
                        success, error_msg = send_email(EMAIL_USER, EMAIL_PASS, recipient_email, subject, st.session_state.complaint_draft)
                        if success:
                            st.success("Email sent successfully! ✅")
                        else:
                            st.error(f"Failed to send email: {error_msg}")

render_footer()