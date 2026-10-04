import html
import io
import random

import streamlit as st
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Thank You, Teacher", page_icon="🍎", layout="centered")

DESIGNER = "Waheed Ali Hamouzai"
FONTS = (
    "https://fonts.googleapis.com/css2?family=Caveat:wght@600;700"
    "&family=Nunito:wght@400;600;800&display=swap"
)

# ---------- Card styles (used on the page and in the downloaded .html) ----------
CARD_CSS = """
.board{position:relative;background:#1E3B2C;color:#F4F2E8;border:14px solid #8B5E3C;border-radius:8px;
  padding:1.8rem 1.6rem 0;box-shadow:0 10px 30px rgba(30,59,44,.35), inset 0 0 60px rgba(0,0,0,.45);text-align:center;overflow:hidden}
.board::before{content:"";position:absolute;inset:8px;border:2px dashed rgba(244,242,232,.28);border-radius:4px;pointer-events:none}
.board .ribbon{display:inline-block;background:#F0B429;color:#1E3B2C;font-family:'Nunito',sans-serif;font-weight:800;
  font-size:.78rem;letter-spacing:.06em;padding:.3rem 1.1rem;border-radius:3px}
.board .star{color:#F4F2E8;font-size:1.3rem;margin-top:.5rem}
.board .head{font-family:'Caveat',cursive;font-size:3rem;color:#F0B429;line-height:1.05}
.board .to{font-family:'Caveat',cursive;font-size:1.9rem;margin-top:.2rem}
.board hr{border:0;border-top:2px dashed rgba(244,242,232,.35);margin:.8rem auto;width:60%}
.board .msg{font-family:'Caveat',cursive;font-size:1.65rem;line-height:1.4;max-width:34rem;margin:.5rem auto}
.board .ps{font-family:'Caveat',cursive;font-size:1.35rem;opacity:.85}
.board .hadith{background:rgba(244,242,232,.07);border:2px solid rgba(240,180,41,.55);border-radius:6px;
  padding:.8rem 1.1rem;margin:1.1rem auto .4rem;max-width:34rem;text-align:left}
.board .hadith .q{font-family:'Caveat',cursive;font-size:1.4rem;line-height:1.3;font-style:italic}
.board .hadith .ref{font-family:'Nunito',sans-serif;font-weight:800;font-size:.8rem;color:#F0B429;margin-top:.35rem}
.board .from{font-family:'Caveat',cursive;font-size:1.8rem;color:#F0B429;text-align:right;margin-top:.8rem;line-height:1.1}
.board .from small{display:block;font-size:1.15rem;color:#F4F2E8;opacity:.8}
.board .tray{background:#8B5E3C;margin:1.1rem -1.6rem 0;padding:.45rem 1rem;display:flex;justify-content:space-between;
  align-items:center;font-family:'Nunito',sans-serif;font-size:.78rem;color:#F4F2E8}
.board .tray .chalk{display:inline-block;width:26px;height:8px;background:#F4F2E8;border-radius:2px;margin-right:6px}
.board .tray .chalk.y{background:#F0B429}
"""

PAGE_CSS = f"""
@import url('{FONTS}');
html, body, [class*="css"], .stApp {{ font-family:'Nunito',sans-serif; }}
.stApp {{ background:#E9F0EA; }}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ max-width:760px; padding-top:1.8rem; }}
.hero {{ text-align:center; margin-bottom:1.2rem; }}
.hero .pill {{ display:inline-block; background:#1E3B2C; color:#F0B429; font-weight:800; font-size:.8rem;
  padding:.3rem 1rem; border-radius:20px; margin-bottom:.5rem; }}
.hero h1 {{ font-family:'Caveat',cursive; font-size:3.6rem; color:#1E3B2C; margin:0; line-height:1; }}
.hero p {{ color:#3d5246; margin:.4rem auto 0; max-width:30rem; }}
div[data-testid="stForm"] {{ background:#fff; border:2px solid #1E3B2C; border-radius:10px; padding:1.2rem 1.4rem; }}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{
  background:#F0B429; color:#1E3B2C; border:2px solid #1E3B2C; border-radius:8px; font-weight:800; }}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {{
  background:#1E3B2C; color:#F0B429; border-color:#1E3B2C; }}
.wall-title {{ font-family:'Caveat',cursive; font-size:2.1rem; color:#1E3B2C; margin:1.8rem 0 .4rem; }}
.note {{ background:#fff; border-left:6px solid #F0B429; border-radius:6px; padding:.6rem .9rem; margin-bottom:.5rem; color:#26382e; }}
.note b {{ color:#1E3B2C; }}
.credit {{ text-align:center; margin:2.2rem 0 .5rem; color:#3d5246; font-size:.9rem; }}
.credit b {{ color:#1E3B2C; }}
{CARD_CSS}
"""
st.markdown(f"<style>{PAGE_CSS}</style>", unsafe_allow_html=True)

# ---------- Content ----------
HONORIFICS = ["Sir", "Miss", "Madam", "Ustad ji", "Ustani ji", "Name only"]

MESSAGES = {
    "Heartfelt": [
        "Dear {t}, thank you for teaching me not just lessons, but patience, honesty and self-belief. Whatever I achieve in life will carry a little of your effort and your duas. Happy World Teachers' Day!",
        "{t}, you saw something in me before I did. Thank you for every correction, every encouragement and every minute you gave beyond the syllabus. Happy Teachers' Day!",
    ],
    "Funny": [
        "Dear {t}, thank you for believing in us even when we forgot our homework (again). Class would be incomplete without you. Happy Teachers' Day!",
        "{t}, thank you for staying calm when we said the dog ate our notebook. You are the real hero of every class. Happy Teachers' Day!",
    ],
    "Short and sweet": [
        "Some people teach lessons, you taught life. Thank you, {t}. Happy Teachers' Day!",
        "A good teacher lights a thousand candles without losing a single flame. Thank you, {t}!",
    ],
}

HADITHS = {
    "Teach and be taught": (
        "The best among you are those who learn the Qur'an and teach it.",
        "Sahih al-Bukhari 5027",
    ),
    "Blessings for the teacher": (
        "Allah, His angels, and all creatures in the heavens and the earth, even the ant in its hole "
        "and the fish in the sea, send blessings upon the one who teaches people goodness.",
        "Jami' at-Tirmidhi 2685",
    ),
    "Gratitude to people": (
        "Whoever does not thank people has not thanked Allah.",
        "Sunan Abi Dawud 4811",
    ),
}


@st.cache_resource
def wall():
    """Wishes from all visitors, kept while the server is running."""
    return []


def esc(s):
    return html.escape(s.strip())


def latin(s):
    """Built-in PDF fonts only support Latin-1, so tidy up other characters."""
    for a, b in {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-", "\u2014": "-"}.items():
        s = s.replace(a, b)
    return s.strip().encode("latin-1", "replace").decode("latin-1")


def card_html(w):
    ps = f'<div class="ps">P.S. {esc(w["extra"])}</div>' if w["extra"] else ""
    school = f"<small>{esc(w['school'])}</small>" if w["school"] else ""
    return f"""
<div class="board">
  <span class="ribbon">WORLD TEACHERS' DAY &nbsp;|&nbsp; 5 OCTOBER</span>
  <div class="star">&#9733;</div>
  <div class="head">Happy Teachers' Day!</div>
  <div class="to">For {esc(w['t'])}</div>
  <hr>
  <div class="msg">{esc(w['msg'])}</div>
  {ps}
  <div class="hadith">
    <div class="q">&ldquo;{esc(w['hadith_text'])}&rdquo;</div>
    <div class="ref">Hadith: {esc(w['hadith_ref'])}</div>
  </div>
  <div class="from">&mdash; {esc(w['student'])}{school}</div>
  <div class="tray"><span><span class="chalk"></span><span class="chalk y"></span></span>
    <span>Designed by {DESIGNER}</span></div>
</div>"""


def card_file(w):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Teachers' Day Wish</title><link href="{FONTS}" rel="stylesheet">
<style>body{{background:#E9F0EA;margin:0;padding:1.5rem}}.wrap{{max-width:660px;margin:auto}}{CARD_CSS}</style>
</head><body><div class="wrap">{card_html(w)}</div></body></html>"""


def card_pdf(w):
    buf = io.BytesIO()
    W, H = landscape(A4)
    c = canvas.Canvas(buf, pagesize=(W, H))
    m = 28
    c.setFillColor(HexColor("#E9F0EA")); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor("#8B5E3C")); c.roundRect(m, m, W - 2 * m, H - 2 * m, 6, fill=1, stroke=0)
    c.setFillColor(HexColor("#1E3B2C")); c.rect(m + 14, m + 14, W - 2 * m - 28, H - 2 * m - 28, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#F4F2E8")); c.setLineWidth(0.8); c.setDash(4, 4)
    c.rect(m + 26, m + 26, W - 2 * m - 52, H - 2 * m - 52, fill=0, stroke=1); c.setDash()

    def centre(txt, y, font, size, color):
        c.setFont(font, size); c.setFillColor(HexColor(color)); c.drawCentredString(W / 2, y, txt)

    def para(txt, y, font, size, color, width, lead):
        c.setFont(font, size); c.setFillColor(HexColor(color))
        for line in simpleSplit(txt, font, size, width):
            c.drawCentredString(W / 2, y, line); y -= lead
        return y

    centre("WORLD TEACHERS' DAY  |  5 OCTOBER", 505, "Helvetica-Bold", 10, "#F0B429")
    centre("Happy Teachers' Day!", 462, "Times-BoldItalic", 38, "#F0B429")
    centre(latin(f"For {w['t']}"), 428, "Times-Italic", 20, "#F4F2E8")
    c.setStrokeColor(HexColor("#F4F2E8")); c.setDash(3, 3); c.line(W / 2 - 150, 412, W / 2 + 150, 412); c.setDash()
    y = para(latin(w["msg"]), 390, "Times-Italic", 16, "#F4F2E8", 620, 22)
    if w["extra"].strip():
        y = para("P.S. " + latin(w["extra"]), y - 2, "Times-Italic", 13, "#F4F2E8", 620, 18)

    lines = simpleSplit(latin(w["hadith_text"]), "Times-Italic", 12, 560)
    bh = len(lines) * 15 + 38
    top = y - 6
    c.setFillColor(HexColor("#2B503D")); c.setStrokeColor(HexColor("#F0B429")); c.setLineWidth(1.2)
    c.roundRect(W / 2 - 300, top - bh, 600, bh, 6, fill=1, stroke=1)
    ty = top - 20
    c.setFont("Times-Italic", 12); c.setFillColor(HexColor("#F4F2E8"))
    for line in lines:
        c.drawString(W / 2 - 280, ty, line); ty -= 15
    c.setFont("Helvetica-Bold", 9); c.setFillColor(HexColor("#F0B429"))
    c.drawString(W / 2 - 280, ty - 2, "Hadith: " + latin(w["hadith_ref"]))

    c.setFont("Times-BoldItalic", 18); c.setFillColor(HexColor("#F0B429"))
    c.drawRightString(W - m - 44, 112, "- " + latin(w["student"]))
    if w["school"].strip():
        c.setFont("Helvetica", 10); c.setFillColor(HexColor("#F4F2E8"))
        c.drawRightString(W - m - 44, 97, latin(w["school"]))
    centre(f"Designed by {DESIGNER}", 66, "Helvetica-Oblique", 9, "#F4F2E8")
    c.showPage(); c.save()
    return buf.getvalue()


# ---------- Page ----------
st.markdown(
    """<div class="hero">
<div class="pill">5 OCTOBER &nbsp;|&nbsp; WORLD TEACHERS' DAY</div>
<h1>Say thank you to your teacher</h1>
<p>Fill in a few details and get a chalkboard card with a heartfelt message and a hadith on honouring teachers.</p>
</div>""",
    unsafe_allow_html=True,
)

with st.form("wish_form"):
    c1, c2 = st.columns(2)
    student = c1.text_input("Your name", placeholder="e.g. Hamza Ali")
    school = c2.text_input("Class or school (optional)", placeholder="e.g. Class 9, Government High School")
    c3, c4 = st.columns([1, 2])
    honor = c3.selectbox("You call your teacher", HONORIFICS)
    teacher = c4.text_input("Teacher's name", placeholder="e.g. Ahmed")
    c5, c6 = st.columns(2)
    tone = c5.radio("Message style", list(MESSAGES))
    hkey = c6.radio("Hadith for your card", list(HADITHS))
    extra = st.text_input("Add your own line (optional)", max_chars=140, placeholder="e.g. I will never forget your Friday quizzes")
    go = st.form_submit_button("Create my card", use_container_width=True)

if go:
    if not student.strip() or not teacher.strip():
        st.error("Please enter your name and your teacher's name.")
    else:
        t = teacher.strip() if honor == "Name only" else f"{honor} {teacher.strip()}"
        msg = random.choice(MESSAGES[tone]).format(t=t)
        htext, href = HADITHS[hkey]
        st.session_state["wish"] = dict(
            student=student, school=school, t=t, msg=msg, extra=extra,
            hadith_text=htext, hadith_ref=href,
        )
        wall().append({"student": student.strip(), "t": t})
        st.balloons()

w = st.session_state.get("wish")
if w:
    st.markdown(card_html(w), unsafe_allow_html=True)
    st.write("")
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download as PDF", card_pdf(w), "teachers_day_card.pdf", "application/pdf", use_container_width=True)
    d2.download_button("Download as web page", card_file(w), "teachers_day_card.html", "text/html", use_container_width=True)
    d3.button("Write another message", on_click=lambda: st.session_state.pop("wish", None), use_container_width=True)

st.markdown('<div class="wall-title">Wishes so far</div>', unsafe_allow_html=True)
recent = wall()[-12:][::-1]
if not recent:
    st.caption("No wishes yet. Yours can be the first.")
for n in recent:
    st.markdown(
        f'<div class="note"><b>{esc(n["student"])}</b> thanked {esc(n["t"])}</div>',
        unsafe_allow_html=True,
    )

st.markdown(f'<div class="credit">Designed by <b>{DESIGNER}</b></div>', unsafe_allow_html=True)
