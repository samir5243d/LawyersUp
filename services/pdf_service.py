import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
