import os
import streamlit as st


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

ALL_CATEGORIES = list(CATEGORY_AUTHORITY_MAP.keys())
