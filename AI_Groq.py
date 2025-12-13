import streamlit as st
import time
from dotenv import load_dotenv
import os
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
import io

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Make sure your env var is named correctly
#client = openai.OpenAI(api_key=OPENAI_API_KEY)

client = Groq(api_key=GROQ_API_KEY)


NCERT_BOOKS = {
    1: {
        "English": {
            "Mridang": {
                "url": "https://ncert.nic.in/textbook.php?aemr1=0-9",
                "chapters": [
                    "Two Little Hands",
                    "Greetings",
                    "Picture Time",
                    "The Cap-seller and the Monkeys",
                    "A Farm",
                    "Fun with Pictures",
                    "The Food we Eat",
                    "The Four Seasons",
                    "Anandi's Rainbow"
                ]
            }
        },
        "Maths": {
            "Joyful-Mathematics": {
                "url": "https://ncert.nic.in/textbook.php?aejm1=0-13",
                "chapters": [
                    "Chapter 1: Pre-number Concepts",
                    "Chapter 2: Shapes",
                    "Chapter 3: Numbers 1 to 9",
                    "Chapter 4: Numbers 10 to 20",
                    "Chapter 5: Addition and Subtraction of single digit",
                    "Chapter 6: Addition and Subtraction up to 20",
                    "Chapter 7: Measurements",
                    "Chapter 8: Numbers 21 to 99",
                    "Chapter 9: Patterns",
                    "Chapter 10: Time",
                    "Chapter 11: Multiplication",
                    "Chapter 12: Money",
                    "Chapter 13: Data Handling"
                ]
            }
        },
        "Hindi": {
            "Sarangi": {
                "url": "https://ncert.nic.in/textbook.php?ahsr1=0-19",
                "chapters": [
                    "Chapter 1: Meena ka Pariwar",
                    "Chapter 1.1: Chanda Mama Door ke",
                    "Chapter 2: Dada Dadi",
                    "Chapter 3: Reena ka Din",
                    "Chapter 4: Rani Bhi",
                    "Chapter 4.1: Murga bola Kukdu-ku",
                    "Chapter 5: Mithai",
                    "Chapter 6: Teen Sathi",
                    "Chapter 7: Wah, Mere Ghode!",
                    "Chapter 8 : Khatare mein Saamp",
                    "Chapter 8.1: Khabari Jhabari Bakari",
                    "Chapter 9: Aloo ki Sadak",
                    "Chapter 10: Jhulam Jhuli",
                    "Chapter 11: Bhutte",
                    "Chapter 12: Phuli Roti",
                    "Chapter 13: Mela",
                    "Chapter 14: Burka Aur Megha",
                    "Chapter 15: Holi",
                    "Chapter 16: Janmadivas par Ped Lagao",
                    "Chapter 17: Hawa",
                    "Chapter 18: Kitni Pyari hai yeh Duniya",
                    "Chapter 19:Chand ka Baccha",
                    "Chapter 19.1: Akshar Geeth"
                ]
            }
        }
    },

    2: {
        "English": {
            "Mridang": {
                "url": "https://ncert.nic.in/textbook.php?bemr1=0-13",
                "chapters": ["Chapter 1", "Chapter 2"]
            }
        },
        "Maths": {
            "Joyful-Mathematics": {
                "url": "https://ncert.nic.in/textbook.php?bejm1=0-11",
                "chapters": ["Chapter 1", "Chapter 2"]
            }
        },
        "Hindi": {
            "Sarangi": {
                "url": "https://ncert.nic.in/textbook.php?bhsr1=0-26",
                "chapters": ["Chapter 1", "Chapter 2"]
            }
        }
    }
}


# -------------------------------------------------------
# AI FUNCTION
# -------------------------------------------------------
def request_analyzer(selected_class, selected_subject, selected_textbook,
                     selected_chapters, selected_marks, paper_count):

    reference_url = NCERT_BOOKS[selected_class][selected_subject][selected_textbook]["url"]

    prompt = f"""
    You are a highly experienced Indian school exam paper generator.

    Generate {paper_count} distinct QUESTION PAPERS for:

    • Class: {selected_class}
    • Subject: {selected_subject}
    • Textbook: {selected_textbook}
    • Chapters: {", ".join(selected_chapters)}
    • Total Marks: {selected_marks}
    • Reference URL: {reference_url}

    PAPER FORMAT (MUST FOLLOW):

    1️⃣ SECTION A – MCQs (20% Marks)
    - 1 mark each
    - 4 options per question
    - Only one correct answer

    2️⃣ SECTION B – Fill in the Blanks (10% Marks)

    3️⃣ SECTION C – True/False (10% Marks)

    4️⃣ SECTION D – Short Answer Questions (35% Marks)
    - 2–4 mark questions
    - Crisp answers expected

    5️⃣ SECTION E – Long Answer Questions (25% Marks)
    - 5–8 marks
    - Must be detailed

    DIFFICULTY LEVEL:
    • 50% Easy
    • 40% Medium
    • 10% Hard

    REQUIREMENTS:
    - NUMBER every question
    - Balance marks to exactly total {selected_marks}
    - DO NOT repeat questions across different papers
    - Each paper must be fully separated with:
        --- PAPER {{n}} START ---
        --- PAPER {{n}} END ---

    Format beautifully for student printing.
    """

    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=4000
    )
    return response.choices[0].message.content

def generate_styled_pdf(title, text):
    """
    Generate a fully formatted multi-page PDF with:
    - Title
    - Headers / footers
    - Auto line wrapping
    - Clean spacing
    - Page numbers
    - Section formatting
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=72,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Title'],
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor("#1A237E"),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        'section_style',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0D47A1"),
        spaceBefore=12,
        spaceAfter=10
    )

    text_style = ParagraphStyle(
        'text_style',
        parent=styles['Normal'],
        fontSize=11,
        leading=16
    )

    # Document story content
    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 14))

    # Split into sections based on paper separators
    for line in text.split("\n"):
        if line.strip().startswith("SECTION"):
            story.append(Paragraph(f"<b>{line}</b>", section_style))
        else:
            story.append(Paragraph(line.replace(" ", "&nbsp;"), text_style))
        story.append(Spacer(1, 4))

    # Page number callback
    def add_page_numbers(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(A4[0] - 40, 20, text)

    doc.build(story, onLaterPages=add_page_numbers, onFirstPage=add_page_numbers)

    buffer.seek(0)
    return buffer
# -------------------------------------------------------
# STREAMLIT UI  (Fixed)
# -------------------------------------------------------
def app():

    st.set_page_config(
        page_title="NCERT Q-Genie",
        layout="centered"
    )

    st.title("📚 NCERT Q-Genie")
    st.markdown("### Generate sample question papers for NCERT")

    # ------------------ DYNAMIC DROPDOWNS ------------------

    # Class (always first)
    selected_class = st.selectbox(
        "Select Class",
        list(NCERT_BOOKS.keys()),
        key="class_select"
    )

    # Subject (depends on class)
    selected_subject = st.selectbox(
        "Select Subject",
        list(NCERT_BOOKS[selected_class].keys()),
        key=f"subject_select_{selected_class}"
    )

    # Textbooks (depends on subject)
    textbook_options = list(NCERT_BOOKS[selected_class][selected_subject].keys())

    selected_textbook = st.selectbox(
        "Select Textbook",
        textbook_options,
        index=0,
        key=f"textbook_select_{selected_class}_{selected_subject}"
    )

    # ------------------ FORM ------------------

    with st.form("qgenie_form"):

        chapters_list = NCERT_BOOKS[selected_class][selected_subject][selected_textbook]["chapters"]

        selected_chapters = st.multiselect(
            "Select Chapters",
            chapters_list,
            default=chapters_list[:2]
        )

        selected_marks = st.selectbox("Total Marks", list(range(20, 101, 10)))
        paper_count = st.selectbox("Number of Papers", list(range(1, 6)))

        submit = st.form_submit_button("🚀 Generate")

    # ------------------ SUBMISSION ------------------

    if submit:
        if not selected_chapters:
            st.error("Please select at least one chapter.")
            return

        with st.spinner("Generating your paper..."):
            output = request_analyzer(
                selected_class,
                selected_subject,
                selected_textbook,
                selected_chapters,
                selected_marks,
                paper_count
    )

        st.success("🎉 Paper Generated Successfully!")
        st.write(output)

        pdf_buffer = generate_styled_pdf(
    title=f"Class {selected_class} – {selected_subject} Question Paper",
    text=output
)

st.download_button(
    label="📄 Download Question Paper (PDF)",
    data=pdf_buffer,
    file_name=f"Class_{selected_class}_{selected_subject}_Paper.pdf",
    mime="application/pdf"
)




# -------------------------------------------------------
# RUN APP
# -------------------------------------------------------
if __name__ == "__main__":
    app()
                
