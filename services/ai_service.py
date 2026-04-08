import requests
import json
from config.settings import GROQ_API_KEY
from utils.helpers import keyword_detect_category, get_authority_for_category

def analyze_legal_issue(user_input, manual_category, ALL_CATEGORIES, selected_language):
    """Encapsulates the Groq API call for initial legal analysis."""
    
    if not GROQ_API_KEY:
        return {"success": False, "error": "GROQ_API_KEY is missing. Please ensure it is set in your .env file."}
        
    category_list_str = ", ".join([f'"{c}"' for c in ALL_CATEGORIES])
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
        "messages": [{"role": "user", "content": prompt}],
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
                
                if ai_category in ["Unknown Category", "Other", ""]:
                    kw_cat = keyword_detect_category(user_input)
                    if kw_cat != "Other":
                        ai_category = kw_cat
                
                if manual_category != "Auto-Detect":
                    final_category = manual_category
                else:
                    final_category = ai_category
                
                if ai_authority and ai_authority != "N/A":
                    final_authority = ai_authority
                else:
                    final_authority = get_authority_for_category(final_category)
                    
                return {
                    "success": True,
                    "category": final_category,
                    "recommended_authority": final_authority,
                    "llm_response": parsed_reply.get("response", raw_reply)
                }
                
            except json.JSONDecodeError:
                fallback_cat = keyword_detect_category(user_input)
                final_category = fallback_cat if manual_category == "Auto-Detect" else manual_category
                return {
                    "success": True, 
                    "category": final_category, 
                    "recommended_authority": get_authority_for_category(final_category), 
                    "llm_response": raw_reply
                }
        else:
            return {"success": False, "error": "API returned an unexpected format.", "details": result}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Network or API Error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"An unexpected error occurred: {e}"}


def generate_complaint_draft(category, custom_authority, custom_doc_type, default_tone, p_details, user_problem, language):
    """Encapsulates the Groq API call for generating the complaint document."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    personal_details = f"""
    Name: {p_details['p_name'].strip() if p_details['p_name'].strip() else '[Your Name]'}
    Age: {p_details['p_age'].strip() if p_details['p_age'].strip() else '[Your Age]'}
    Address: {p_details['p_address'].strip() if p_details['p_address'].strip() else '[Your Address]'}
    Phone Number: {p_details['p_phone'].strip() if p_details['p_phone'].strip() else '[Your Phone Number]'}
    Email: {p_details['p_email'].strip() if p_details['p_email'].strip() else '[Your Email]'}
    Date: {p_details['p_date'].strftime('%d-%m-%Y')}
    Incident Location: {p_details['p_location'].strip() if p_details['p_location'].strip() else '[Location]'}
    Police Station Name: {p_details['p_police'].strip() if p_details['p_police'].strip() else '[Police Station Name]'}
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
    
    The entire generated draft MUST be written fluently in {language}.
    
    Category: {category}
    User's Specific Problem: {user_problem}
    
    Output ONLY the formal document itself. Do NOT include any conversational text, explanations, or introductory remarks like "Here is your draft".
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": draft_prompt}],
        "temperature": 0.4
    }
    
    try:
        c_resp = requests.post(url, headers=headers, json=payload)
        c_resp.raise_for_status()
        c_result = c_resp.json()
        
        if "choices" in c_result and len(c_result["choices"]) > 0:
            return {"success": True, "draft": c_result["choices"][0]["message"]["content"]}
        else:
            return {"success": False, "error": "Failed to generate draft."}
    except Exception as e:
        return {"success": False, "error": f"Drafting error: {e}"}
