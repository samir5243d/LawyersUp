
import streamlit as st
st.set_page_config(page_title="Lawyer's Up - AI Legal Assistant", page_icon="⚖️", layout="wide")
import requests
import os
import json
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ═══════════════════════════════════════════════════════════════
# CATEGORY → AUTHORITY MAPPING (Dynamic)
# ═══════════════════════════════════════════════════════════════

CATEGORY_AUTHORITY_MAP = {
    "Cybercrime": {
        "default_authority": "The Station House Officer, Cyber Crime Cell",
        "doc_type": "FIR (Cybercrime)",
        "tone": "Strict, formal, and urgent",
        "keywords": ["hack", "phishing", "online fraud", "cyber", "data breach", "identity theft", "social media", "dark web", "ransomware", "malware", "password", "otp"],
    },
    "Fraud": {
        "default_authority": "The Station House Officer, Local Police Station / Cyber Cell",
        "doc_type": "FIR / Criminal Complaint",
        "tone": "Strict, detailed, and formal",
        "keywords": ["fraud", "scam", "cheated", "money", "forged", "fake", "ponzi", "chit fund", "investment scam", "impersonation"],
    },
    "Harassment (College)": {
        "default_authority": "The Principal / Head of Institution",
        "doc_type": "Formal Complaint to College Authority",
        "tone": "Formal, serious, and precise",
        "keywords": ["college", "professor", "ragging", "university", "campus", "hostel", "dean", "teacher", "student", "academic", "semester", "exam"],
    },
    "Harassment (General)": {
        "default_authority": "The Station House Officer, Local Police Station",
        "doc_type": "FIR / Formal Complaint",
        "tone": "Firm, serious, and formal",
        "keywords": ["stalking", "threat", "intimidation", "bully", "defamation", "neighbour", "neighbor", "verbal abuse"],
    },
    "Workplace Complaints": {
        "default_authority": "HR Department / Internal Complaints Committee (ICC)",
        "doc_type": "Formal Workplace Complaint",
        "tone": "Professional, firm, and detailed",
        "keywords": ["office", "employer", "hr", "workplace", "salary", "termination", "wrongful", "boss", "manager", "company", "employee", "posh", "internal committee", "appraisal", "promotion"],
    },
    "Women Safety": {
        "default_authority": "The Station House Officer / Women Helpline / National Commission for Women",
        "doc_type": "FIR / Complaint to Women Cell",
        "tone": "Urgent, serious, and empathetic",
        "keywords": ["women", "dowry", "domestic violence", "eve teasing", "molestation", "sexual harassment", "stalking women", "acid attack", "婚", "498a", "protection of women"],
    },
    "Consumer Issues": {
        "default_authority": "Customer Support / District Consumer Disputes Redressal Forum",
        "doc_type": "Consumer Complaint",
        "tone": "Firm, requesting resolution or compensation",
        "keywords": ["product", "refund", "defective", "warranty", "e-commerce", "delivery", "service", "consumer", "overcharged", "misleading", "adulteration", "advertisement"],
    },
    "Government / RTI Issues": {
        "default_authority": "Public Information Officer (PIO) / Concerned Government Department",
        "doc_type": "RTI Application / Formal Complaint to Government",
        "tone": "Formal, respectful, and rights-aware",
        "keywords": ["rti", "right to information", "government", "corruption", "bribe", "public office", "municipality", "ration", "passport", "license", "permit", "sarkari", "neta", "politician"],
    },
    "Banking / Financial Issues": {
        "default_authority": "Branch Manager / Banking Ombudsman / RBI",
        "doc_type": "Formal Bank Complaint / Ombudsman Complaint",
        "tone": "Precise, formal, and factual",
        "keywords": ["bank", "loan", "emi", "credit card", "debit card", "upi", "transaction", "interest", "rbi", "ombudsman", "insurance", "neft", "rtgs", "cheque", "account frozen", "atm"],
    },
    "Public / Municipal Issues": {
        "default_authority": "Municipal Commissioner / Municipal Corporation",
        "doc_type": "Complaint to Municipal Corporation",
        "tone": "Formal, civic-minded, and assertive",
        "keywords": ["road", "pothole", "water supply", "drainage", "garbage", "sewage", "streetlight", "encroachment", "building permit", "noise pollution", "stray animals", "footpath", "municipality"],
    },
}

# A flat list of category names for the dropdown
ALL_CATEGORIES = list(CATEGORY_AUTHORITY_MAP.keys())

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def send_email(sender, password, recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)

def generate_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    story = []
    
    for p_text in text.split('\n'):
        if p_text.strip() == '':
            story.append(Spacer(1, 12))
            continue
            
        # Escape XML characters for reportlab
        safe_text = p_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Remove bold markdown since we aren't parsing complex tags here
        safe_text = safe_text.replace('**', '')
        
        p = Paragraph(safe_text, styles["Normal"])
        story.append(p)
        story.append(Spacer(1, 4))
        
    doc.build(story)
    buffer.seek(0)
    return buffer


def keyword_detect_category(text: str) -> str:
    """
    Simple keyword-based fallback to detect category from user input text.
    Returns the best-matching category name, or 'Other' if nothing matches.
    """
    text_lower = text.lower()
    scores = {}
    for cat, info in CATEGORY_AUTHORITY_MAP.items():
        score = sum(1 for kw in info["keywords"] if kw in text_lower)
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "Other"


def get_authority_for_category(category: str) -> str:
    """Get the default authority for a given category."""
    if category in CATEGORY_AUTHORITY_MAP:
        return CATEGORY_AUTHORITY_MAP[category]["default_authority"]
    return "The Respective Authority"


def get_doc_type_for_category(category: str) -> str:
    """Get the default document type for a given category."""
    if category in CATEGORY_AUTHORITY_MAP:
        return CATEGORY_AUTHORITY_MAP[category]["doc_type"]
    return "Formal Legal Complaint"


def get_tone_for_category(category: str) -> str:
    """Get the default tone for a given category."""
    if category in CATEGORY_AUTHORITY_MAP:
        return CATEGORY_AUTHORITY_MAP[category]["tone"]
    return "Formal and professional"


# ═══════════════════════════════════════════════════════════════
# LOAD ENVIRONMENT VARIABLES
# ═══════════════════════════════════════════════════════════════

load_dotenv()

def get_secret(key):
    """Retrieve secret from Streamlit secrets first, then fallback to os.getenv for local dev."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key)

GROQ_API_KEY = get_secret("GROQ_API_KEY")
EMAIL_USER = get_secret("EMAIL_USER")
EMAIL_PASS = get_secret("EMAIL_PASS")

# ═══════════════════════════════════════════════════════════════
# SIDEBAR UI
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("⚖️ Lawyer's Up")
    st.markdown("##### Your AI-Powered Legal Assistant")

    st.markdown("---")

    st.markdown("*🗺️ How It Works*")
    st.markdown(
        """
<div style="
    background: linear-gradient(135deg, #1a1f2e, #0f1422);
    border: 1px solid #2e3650;
    border-radius: 12px;
    padding: 16px 18px;
    margin-top: 6px;
">
  <div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 10px;">
    <span style="font-size: 1.2em;">📝</span>
    <div>
      <strong style="color: #e0e6ff;">Enter your problem</strong><br>
      <span style="color: #8892b0; font-size: 0.85em;">Describe your legal issue in your own words</span>
    </div>
  </div>
  <div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 10px;">
    <span style="font-size: 1.2em;">🤖</span>
    <div>
      <strong style="color: #e0e6ff;">AI analyzes your case</strong><br>
      <span style="color: #8892b0; font-size: 0.85em;">Detects category & the right authority</span>
    </div>
  </div>
  <div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 10px;">
    <span style="font-size: 1.2em;">📄</span>
    <div>
      <strong style="color: #e0e6ff;">Generate complaint / FIR</strong><br>
      <span style="color: #8892b0; font-size: 0.85em;">Auto-drafted formal legal document</span>
    </div>
  </div>
  <div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 10px;">
    <span style="font-size: 1.2em;">⬇️</span>
    <div>
      <strong style="color: #e0e6ff;">Download as PDF</strong><br>
      <span style="color: #8892b0; font-size: 0.85em;">Save a ready-to-submit document</span>
    </div>
  </div>
  <div style="display: flex; align-items: flex-start; gap: 10px;">
    <span style="font-size: 1.2em;">📧</span>
    <div>
      <strong style="color: #e0e6ff;">Send via Email</strong><br>
      <span style="color: #8892b0; font-size: 0.85em;">Mail directly to the authority</span>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("🌐 Language Setup")
    selected_language = st.selectbox("Preferred / प्राधान्य / पसंदीदा :", ["English", "Hindi", "Marathi"])

# ═══════════════════════════════════════════════════════════════
# MAIN UI
# ═══════════════════════════════════════════════════════════════

st.title("🏛️ Lawyer's Up : Legal AI Assistant")
st.markdown("Describe your issue below to instantly receive professional legal guidance. 🚀")

# Category selector dropdown
cat_col1, cat_col2 = st.columns([1.5, 3.5])
with cat_col1:
    manual_category = st.selectbox(
        "📂 Select Complaint Category",
        ["Auto-Detect"] + ALL_CATEGORIES,
        help="Choose a category or let AI auto-detect from your description."
    )
with cat_col2:
    # Show auto-filled authority based on category selection
    if manual_category != "Auto-Detect":
        auto_authority = get_authority_for_category(manual_category)
        st.text_input(
            "🏢 Recommended Authority (auto-filled)",
            value=auto_authority,
            disabled=True,
            help="This authority is auto-filled based on your selected category."
        )
    else:
        st.text_input(
            "🏢 Recommended Authority",
            value="Will be detected from your description",
            disabled=True,
            help="Select a category or let AI determine the appropriate authority."
        )

# User input text area
user_input = st.text_area("✍️ *Enter your problem:*", height=150, placeholder="E.g., I was defrauded of money online by a fake e-commerce website...")

col1, col2 = st.columns([1, 4])
with col1:
    get_help_btn = st.button("✨ Get Legal Help", use_container_width=True)

if get_help_btn:
    # Input validation
    if not user_input.strip():
        st.warning("Please enter your problem before submitting.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY is missing. Please ensure it is set in your .env file.")
    else:
        with st.spinner("Analyzing your issue..."):
            
            # Build the list of valid categories for the AI prompt
            category_list_str = ", ".join([f'"{c}"' for c in ALL_CATEGORIES])
            
            # If user manually selected a category, hint that to the AI
            category_hint = ""
            if manual_category != "Auto-Detect":
                category_hint = f'\nIMPORTANT HINT: The user has pre-selected the category "{manual_category}". Use this as the category unless the problem clearly belongs to a different category.'
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }
            
            prompt = f"""System Instructions:
            You are a helpful and knowledgeable Indian Legal Assistant.
            
            STEP 1 — CATEGORY DETECTION:
            First, carefully analyze the user's problem and classify it into EXACTLY ONE of these categories:
            {category_list_str}, "Other", or "Not a Legal Issue".
            
            Use context and keywords to determine the category. Here are examples:
            - If user mentions college, professor, ragging, campus → "Harassment (College)"
            - If user mentions office, HR, employer, salary → "Workplace Complaints"
            - If user mentions bank, loan, UPI, credit card → "Banking / Financial Issues"
            - If user mentions product, refund, e-commerce → "Consumer Issues"
            - If user mentions hack, phishing, online fraud → "Cybercrime"
            - If user mentions scam, forged documents → "Fraud"
            - If user mentions dowry, domestic violence, eve teasing → "Women Safety"
            - If user mentions RTI, government corruption, bribe → "Government / RTI Issues"
            - If user mentions road, pothole, water, drainage, municipal → "Public / Municipal Issues"
            - For general harassment/stalking/threats → "Harassment (General)"
            
            DO NOT default everything to one single category. Pick the MOST SPECIFIC match.
            {category_hint}
            
            STEP 2 — AUTHORITY ASSIGNMENT:
            Based on the detected category, assign the correct authority from this mapping:
            - Cybercrime → Cyber Crime Cell / Police
            - Fraud → Police / Cyber Cell
            - Harassment (College) → Principal / College Authority
            - Harassment (General) → Local Police Station
            - Workplace Complaints → HR / Internal Complaints Committee (ICC)
            - Women Safety → Police / Women Cell / National Commission for Women
            - Consumer Issues → Consumer Forum / Company Support
            - Government / RTI Issues → Concerned Government Department / PIO
            - Banking / Financial Issues → Bank / RBI Ombudsman
            - Public / Municipal Issues → Municipal Corporation
            - Other → The Respective Authority
            
            STEP 3 — RESPONSE:
            You MUST return your response as a strict JSON object with THREE keys:
            1. "category": The detected category (one of the exact category names above).
            2. "recommended_authority": The correct authority for this category.
            3. "response": Your detailed response in markdown format. ALL TEXT IN THIS RESPONSE MUST BE IN {selected_language}.
            
            If it is NOT a valid legal issue, set "category" to "Not a Legal Issue" and "recommended_authority" to "N/A". In "response", respectfully state (in {selected_language}) that as an Indian legal AI assistant, you need more details, and politely ask them to clarify.
            
            If it IS a valid legal issue, structure the "response" text into these three sections using clean markdown formatting (in {selected_language}):
            
            ### 1. Issue Understanding
            Explain the user's issue in simple language so they know you understand their situation.
            
            ### 2. Legal Explanation
            Provide a simple legal explanation according to Indian law. Avoid complex legal jargon, and if any legal terms are necessary, explain them simply.
            
            ### 3. What You Should Do Next
            Give clear, actionable next steps for the user to solve their problem.
            
            Problem: {user_input}
            """
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "response_format": {"type": "json_object"}
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status() 
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    raw_reply = result["choices"][0]["message"]["content"]
                    try:
                        parsed_reply = json.loads(raw_reply)
                        
                        ai_category = parsed_reply.get("category", "Unknown Category")
                        ai_authority = parsed_reply.get("recommended_authority", "")
                        
                        # If the AI didn't return a valid category, try keyword fallback
                        if ai_category in ["Unknown Category", "Other", ""]:
                            kw_cat = keyword_detect_category(user_input)
                            if kw_cat != "Other":
                                ai_category = kw_cat
                        
                        # If user manually selected a category, prefer that
                        if manual_category != "Auto-Detect":
                            final_category = manual_category
                        else:
                            final_category = ai_category
                        
                        # Set authority: use AI's if available, otherwise derive from mapping
                        if ai_authority and ai_authority != "N/A":
                            final_authority = ai_authority
                        else:
                            final_authority = get_authority_for_category(final_category)
                        
                        st.session_state.category = final_category
                        st.session_state.recommended_authority = final_authority
                        st.session_state.llm_response = parsed_reply.get("response", raw_reply)
                        st.session_state.user_problem = user_input
                        st.session_state.language = selected_language
                        st.session_state.complaint_draft = None  # Reset previous drafts
                        
                    except json.JSONDecodeError:
                        # Fallback: keyword-based detection
                        fallback_cat = keyword_detect_category(user_input)
                        st.session_state.category = fallback_cat if manual_category == "Auto-Detect" else manual_category
                        st.session_state.recommended_authority = get_authority_for_category(st.session_state.category)
                        st.session_state.llm_response = raw_reply
                        st.session_state.user_problem = user_input
                        st.session_state.complaint_draft = None
                        
                else:
                    st.error("API returned an unexpected format.")
                    st.write("Response details:", result)

            except requests.exceptions.RequestException as e:
                st.error(f"Network or API Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# ═══════════════════════════════════════════════════════════════
# DISPLAY: Analysis, Recommended Authority & Complaint Generator
# ═══════════════════════════════════════════════════════════════

if "llm_response" in st.session_state and st.session_state.llm_response:
    st.markdown("---")
    st.subheader("📊 Legal Analysis & Strategy")
    st.success("✅ Analysis Complete!")
    category = st.session_state.category
    recommended_authority = st.session_state.get("recommended_authority", get_authority_for_category(category))
    
    cat_col, auth_col = st.columns([1.5, 3.5])
    with cat_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.success(f"📌 *Detected Category:* {category}")
        else:
            st.warning(f"⚠️ *Detected Category:* {category}")
    with auth_col:
        if category not in ["Not a Legal Issue", "Unknown Category"]:
            st.info(f"🏢 *Recommended Authority:* {recommended_authority}")
        
    st.markdown(st.session_state.llm_response)
    
    # ═══════════════════════════════════════════════════════════════
    # COMPLAINT GENERATOR
    # ═══════════════════════════════════════════════════════════════
    if category not in ["Not a Legal Issue", "Unknown Category"]:
        
        default_type = get_doc_type_for_category(category)
        default_auth = recommended_authority
        default_tone = get_tone_for_category(category)

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

        btn_col, empty_col2 = st.columns([1.5, 3.5])
        with btn_col:
            gen_btn = st.button("🖋️ Generate Draft", use_container_width=True)
            
        if gen_btn:
            with st.spinner(f"Drafting your {category} document..."):
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                }
                
                personal_details = f"""
                Name: {p_name.strip() if p_name.strip() else '[Your Name]'}
                Age: {p_age.strip() if p_age.strip() else '[Your Age]'}
                Address: {p_address.strip() if p_address.strip() else '[Your Address]'}
                Phone Number: {p_phone.strip() if p_phone.strip() else '[Your Phone Number]'}
                Email: {p_email.strip() if p_email.strip() else '[Your Email]'}
                Date: {p_date.strftime('%d-%m-%Y')}
                Incident Location: {p_location.strip() if p_location.strip() else '[Location]'}
                Police Station Name: {p_police.strip() if p_police.strip() else '[Police Station Name]'}
                """
                    
                draft_prompt = f"""
                You are an expert Indian Legal Assistant and an experienced advocate.
                
                DETECTED CATEGORY: {category}
                RECOMMENDED AUTHORITY: {custom_authority}
                
                Your task is to draft a highly professional, specific, and detailed {custom_doc_type} based exactly on the user's situation. 
                The document MUST be explicitly addressed to: {custom_authority}.
                
                CRITICAL INSTRUCTIONS:
                1. DO NOT output a generic template. You MUST write a detailed, narrative-driven complaint using the specific facts provided in the "User's Specific Problem" section below. Extract all possible facts (dates, amounts, actions) from the problem.
                2. Adapt the facts logically into formal Indian legal language. The tone should be: {default_tone}.
                3. Include a precise and professional Subject Line reflecting the severity of the issue.
                4. At the very TOP of the document, include the line:
                   "Recommended Authority: {custom_authority}"
                5. Structure the draft into clear paragraphs:
                   - Introduction (Who is complaining and against whom/what).
                   - Detailed Account of Incident (Chronological narrative based strictly on the user's problem).
                   - Legal Grounds / Impact (The harm or consequences faced by the complainant).
                   - Prayer/Relief Requested (Specific action demanded, such as an immediate investigation, refund, or disciplinary action).
                
                Please seamlessly and naturally integrate the following personal details into the body and the signature block of the draft:
                {personal_details}
                
                IMPORTANT: If any of the personal details above are enclosed in brackets like [Your Name] or [Location], keep them EXACTLY as bracketed placeholders in the text so the user can fill them in later. Do not invent details for placeholders.
                
                The entire generated draft MUST be written fluently in {st.session_state.language}.
                
                Category: {category}
                User's Specific Problem: {st.session_state.user_problem}
                
                Output ONLY the formal document itself. Do NOT include any conversational text, explanations, or introductory remarks like "Here is your draft".
                """
                
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "user", "content": draft_prompt}
                    ],
                    "temperature": 0.4
                }
                
                try:
                    c_resp = requests.post(url, headers=headers, json=payload)
                    c_resp.raise_for_status()
                    c_result = c_resp.json()
                    
                    if "choices" in c_result and len(c_result["choices"]) > 0:
                        st.session_state.complaint_draft = c_result["choices"][0]["message"]["content"]
                    else:
                        st.error("Failed to generate draft.")
                except Exception as e:
                    st.error(f"Drafting error: {e}")
                    
        if st.session_state.get("complaint_draft"):
            st.success("✨ Draft generated successfully!")
            
            col_header, col_copy = st.columns([5, 1])
            with col_header:
                st.markdown("### Step 1: Review Your Complaint")
                st.caption("Review your draft below. Use the copy button in the top-right of the box.")
            with col_copy:
                st.write("") # Spacing alignment
                if st.button("📋 Copy Text", use_container_width=True):
                    st.toast("Copied to clipboard ✅")
            
            # Using st.code() which provides a stable built-in copy button across Streamlit versions
            st.code(st.session_state.complaint_draft, language="text", wrap_lines=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # PDF Download Feature
            pdf_buffer = generate_pdf(st.session_state.complaint_draft)
            st.download_button(
                label="📥 Download as PDF",
                data=pdf_buffer,
                file_name="legal_complaint_draft.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            st.divider()
            
            st.markdown("### Step 2: Send Complaint via Email")
            st.caption("Enter authority email (police, principal, company, etc.)")
            
            recipient_email = st.text_input("Recipient Email Address", placeholder="e.g. support@company.com")
            subject = st.text_input("Email Subject", value="Official Legal Complaint Draft")
            
            st.markdown("<br>", unsafe_allow_html=True)
            send_email_clicked = st.button("🚀 Send Complaint via Email", type="primary", use_container_width=True)
            
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

# --- FOOTER ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.divider()
st.markdown(
    "<div style='text-align: center; color: #888888; font-size: 0.85em; font-weight: 300;'>"
    "Helps generate legal drafts; final verification is done by authorities."
    "</div>", 
    unsafe_allow_html=True
)