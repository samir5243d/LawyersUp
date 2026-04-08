import streamlit as st

def render_sidebar():
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
            """, unsafe_allow_html=True
        )

        st.markdown("---")
        st.subheader("🌐 Language Setup")
        selected_language = st.selectbox("Preferred / प्राधान्य / पसंदीदा :", ["English", "Hindi", "Marathi"])
        return selected_language

def render_footer():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #888888; font-size: 0.85em; font-weight: 300;'>"
        "Helps generate legal drafts; final verification is done by authorities."
        "</div>", 
        unsafe_allow_html=True
    )
