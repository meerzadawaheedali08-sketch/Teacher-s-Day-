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
FONT_URL = (
    "https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Dancing+Script:wght@600;700"
    "&family=Lora:ital,wght@1,500&family=Special+Elite&family=Permanent+Marker&family=Nunito:wght@400;600;800"
    "&family=Noto+Nastaliq+Urdu:wght@400;600&family=Noto+Naskh+Arabic:wght@500&display=swap"
)

# ---------- Options ----------
LANGUAGES = ["English", "Roman Urdu", "Urdu"]

# css family, size multiplier, Urdu family, PDF body font, PDF heading font, PDF body size
FONT_STYLES = {
    "Chalk handwriting": ("'Caveat',cursive", 1.0, "'Noto Nastaliq Urdu',serif", "Times-Italic", "Times-BoldItalic", 16),
    "Elegant script": ("'Dancing Script',cursive", 0.82, "'Noto Nastaliq Urdu',serif", "Times-Italic", "Times-BoldItalic", 16),
    "Classic serif": ("'Lora',serif", 0.68, "'Noto Naskh Arabic',serif", "Times-Roman", "Times-Bold", 15),
    "Clean modern": ("'Nunito',sans-serif", 0.68, "'Noto Naskh Arabic',serif", "Helvetica", "Helvetica-Bold", 14),
    "Typewriter": ("'Special Elite',monospace", 0.66, "'Noto Nastaliq Urdu',serif", "Courier", "Courier-Bold", 13),
    "Bold marker": ("'Permanent Marker',cursive", 0.66, "'Noto Nastaliq Urdu',serif", "Helvetica-Bold", "Helvetica-Bold", 14),
}

NOTEBOOK_LINES = "repeating-linear-gradient(transparent 0 31px, rgba(60,100,170,.22) 31px 32px)"
THEMES = {
    "Classic chalkboard": dict(bg="#1E3B2C", fg="#F4F2E8", accent="#F0B429", frame="#8B5E3C", soft="#2B503D", tray="#F4F2E8", img="none"),
    "Pakistan green": dict(bg="#01411C", fg="#FFFFFF", accent="#CFE8D3", frame="#E8F1EA", soft="#0B5A2E", tray="#01411C", img="none"),
    "Midnight and gold": dict(bg="#14213D", fg="#F1F3F8", accent="#E5B84B", frame="#A67C2E", soft="#1F3159", tray="#FFFFFF", img="none"),
    "Maroon and gold": dict(bg="#4A1420", fg="#FBF1E4", accent="#E3B964", frame="#2B0B12", soft="#5E2230", tray="#FBF1E4", img="none"),
    "School notebook": dict(bg="#FBFBF7", fg="#1F2A44", accent="#B5342A", frame="#1F2A44", soft="#EEF1F8", tray="#FFFFFF", img=NOTEBOOK_LINES),
}
HONORIFICS = {"Sir": "سر", "Miss": "مس", "Madam": "میڈم", "Ustad ji": "استاد جی", "Ustani ji": "استانی جی", "Name only": ""}

LANG_TEXT = {
    "English": dict(ribbon="WORLD TEACHERS' DAY  |  5 OCTOBER", head="Happy Teachers' Day!", to="For {t}", ps="P.S.", hl="Hadith:"),
    "Roman Urdu": dict(ribbon="ALAMI YOUM-E-ASATZA  |  5 OCTOBER", head="Teachers' Day Mubarak!", to="{t} ke naam", ps="P.S.", hl="Hadith:"),
    "Urdu": dict(ribbon="عالمی یومِ اساتذہ  |  ۵ اکتوبر", head="عالمی یومِ اساتذہ مبارک", to="{t} کے نام", ps="نوٹ:", hl="حدیث:"),
}

MESSAGES = {
    "English": {
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
    },
    "Roman Urdu": {
        "Heartfelt": [
            "Respected {t}, aap ne sirf parhaya nahi, zindagi jeena bhi sikhaya. Aap ki mehnat, sabr aur duaon ki wajah se aaj main apne khwab dekhne ke qabil hoon. Teachers' Day mubarak!",
            "{t}, aap ka diya hua ilm hamari sab se bari daulat hai. Shukriya har sabaq ke liye, aur un sab dantoon ke liye jo hamare bhale ke liye thin. Teachers' Day mubarak!",
        ],
        "Funny": [
            "Respected {t}, homework kam dene ki darkhwast apni jagah, magar sach yeh hai ke aap ke baghair hamari class adhoori hai. Teachers' Day mubarak!",
            "{t}, aap ki sab se mushkil khoobi yeh hai ke sawal ka jawab na aane par bhi hamein muskura kar sambhal lete hain. Teachers' Day mubarak!",
        ],
        "Short and sweet": [
            "Jo chiragh ban kar jalte hain, wohi ustad kehlate hain. {t}, aap ko Teachers' Day mubarak!",
        ],
    },
    "Urdu": {
        "Heartfelt": [
            "محترم {t}، آپ کی محنت، صبر اور رہنمائی نے مجھے سکھایا کہ علم صرف کتابوں میں نہیں، کردار میں بھی ہوتا ہے۔ آج میں جو کچھ ہوں، آپ کی تربیت اور دعاؤں کا نتیجہ ہے۔ عالمی یومِ اساتذہ مبارک!",
            "{t}، آپ نے ہمیں صرف پڑھایا نہیں، جینا بھی سکھایا۔ اللہ آپ کو صحت، عزت اور ڈھیروں خوشیاں عطا فرمائے۔ یومِ اساتذہ مبارک!",
        ],
        "Funny": [
            "محترم {t}، ہوم ورک کم دینے کی گزارش اپنی جگہ، مگر سچ یہ ہے کہ آپ کے بغیر ہماری کلاس ادھوری ہے۔ یومِ اساتذہ مبارک!",
        ],
        "Short and sweet": [
            "جو چراغ بن کر جلتے ہیں، وہی استاد کہلاتے ہیں۔ {t}، آپ کو یومِ اساتذہ مبارک!",
        ],
    },
}

# One hadith is picked at random for each card.
HADITHS = [
    dict(
        ref={"English": "Sahih al-Bukhari 5027", "Roman Urdu": "Sahih al-Bukhari 5027", "Urdu": "صحیح بخاری 5027"},
        text={
            "English": "The best among you are those who learn the Qur'an and teach it.",
            "Roman Urdu": "Tum mein sab se behtar woh hai jo Quran seekhe aur sikhaye.",
            "Urdu": "تم میں سب سے بہتر وہ ہے جو قرآن سیکھے اور سکھائے۔",
        },
    ),
    dict(
        ref={"English": "Jami' at-Tirmidhi 2685", "Roman Urdu": "Jami' at-Tirmidhi 2685", "Urdu": "جامع ترمذی 2685"},
        text={
            "English": "Allah, His angels, and all creatures in the heavens and the earth, even the ant in its hole and the fish in the sea, send blessings upon the one who teaches people goodness.",
            "Roman Urdu": "Allah, uske farishte aur aasmanon aur zameen ki har makhlooq, yahan tak ke bil mein cheenti aur samandar mein machhli, logon ko bhalai sikhane wale par rehmat bhejte hain.",
            "Urdu": "اللہ، اس کے فرشتے اور آسمانوں اور زمین کی ہر مخلوق، یہاں تک کہ بل میں چیونٹی اور سمندر میں مچھلی، لوگوں کو بھلائی سکھانے والے پر رحمت بھیجتے ہیں۔",
        },
    ),
    dict(
        ref={"English": "Sunan Abi Dawud 4811", "Roman Urdu": "Sunan Abi Dawud 4811", "Urdu": "سنن ابی داود 4811"},
        text={
            "English": "Whoever does not thank people has not thanked Allah.",
            "Roman Urdu": "Jo logon ka shukr ada nahi karta, woh Allah ka shukr ada nahi karta.",
            "Urdu": "جو لوگوں کا شکر ادا نہیں کرتا، وہ اللہ کا شکر ادا نہیں کرتا۔",
        },
    ),
]

# ---------- Styles ----------
CARD_CSS = """
.board{position:relative;background:var(--bg);background-image:var(--img);color:var(--fg);border:14px solid var(--frame);
  border-radius:8px;padding:1.8rem 1.6rem 0;box-shadow:0 10px 30px rgba(0,0,0,.28), inset 0 0 60px rgba(0,0,0,.22);
  text-align:center;overflow:hidden;font-family:var(--fam)}
.board::before{content:"";position:absolute;inset:8px;border:2px dashed var(--fg);opacity:.3;border-radius:4px;pointer-events:none}
.board .ribbon{display:inline-block;background:var(--accent);color:var(--bg);font-family:'Nunito',sans-serif;font-weight:800;
  font-size:.78rem;letter-spacing:.05em;padding:.3rem 1.1rem;border-radius:3px}
.board .star{font-size:1.3rem;margin-top:.5rem}
.board .head{font-size:calc(3rem*var(--k));color:var(--accent);line-height:1.15}
.board .to{font-size:calc(1.9rem*var(--k));margin-top:.2rem;line-height:1.25}
.board hr{border:0;border-top:2px dashed var(--fg);opacity:.35;margin:.8rem auto;width:60%}
.board .msg{font-size:calc(1.65rem*var(--k));line-height:1.4;max-width:34rem;margin:.5rem auto}
.board .ps{font-size:calc(1.35rem*var(--k));opacity:.85;line-height:1.4}
.board .hadith{background:var(--soft);border:2px solid var(--accent);border-radius:6px;padding:.8rem 1.1rem;
  margin:1.1rem auto .4rem;max-width:34rem;text-align:left}
.board .hadith .q{font-size:calc(1.4rem*var(--k));line-height:1.35}
.board .hadith .ref{font-family:'Nunito',sans-serif;font-weight:800;font-size:.8rem;color:var(--accent);margin-top:.4rem}
.board .from{font-size:calc(1.8rem*var(--k));color:var(--accent);text-align:right;margin-top:.8rem;line-height:1.2}
.board .from small{display:block;font-size:calc(1.15rem*var(--k));color:var(--fg);opacity:.8}
.board .tray{background:var(--frame);color:var(--tray);margin:1.1rem -1.6rem 0;padding:.45rem 1rem;display:flex;
  justify-content:space-between;align-items:center;font-family:'Nunito',sans-serif;font-size:.78rem}
.board .tray .chalk{display:inline-block;width:26px;height:8px;background:#fff;border-radius:2px;margin-right:6px}
.board .tray .chalk.y{background:#F0B429}
.board.ur .msg,.board.ur .hadith{direction:rtl}
.board.ur .hadith{text-align:right}
.board.ur .from{text-align:left}
.board.ur .head,.board.ur .to,.board.ur .msg,.board.ur .ps,.board.ur .hadith .q,.board.ur .from{line-height:2.1}
"""

PAGE_CSS = f"""
@import url('{FONT_URL}');
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


# ---------- Helpers ----------
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
    th, lt = THEMES[w["theme"]], LANG_TEXT[w["lang"]]
    fam, k, ufam = FONT_STYLES[w["font"]][:3]
    ur = w["lang"] == "Urdu"
    style = (f"--bg:{th['bg']};--fg:{th['fg']};--accent:{th['accent']};--frame:{th['frame']};--soft:{th['soft']};"
             f"--tray:{th['tray']};--img:{th['img']};--fam:{ufam if ur else fam};--k:{0.72 if ur else k}")
    ps = f'<div class="ps">{lt["ps"]} {esc(w["extra"])}</div>' if w["extra"].strip() else ""
    school = f"<small>{esc(w['school'])}</small>" if w["school"].strip() else ""
    return f"""
<div class="board{' ur' if ur else ''}" style="{style}">
  <span class="ribbon">{lt['ribbon']}</span>
  <div class="star">&#9733;</div>
  <div class="head">{lt['head']}</div>
  <div class="to">{lt['to'].format(t=esc(w['t']))}</div>
  <hr>
  <div class="msg">{esc(w['msg'])}</div>
  {ps}
  <div class="hadith">
    <div class="q">&ldquo;{esc(w['hadith_text'])}&rdquo;</div>
    <div class="ref">{lt['hl']} {esc(w['hadith_ref'])}</div>
  </div>
  <div class="from">&mdash; {esc(w['student'])}{school}</div>
  <div class="tray"><span><span class="chalk"></span><span class="chalk y"></span></span>
    <span>Designed by {DESIGNER}</span></div>
</div>"""


def card_file(w):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Teachers' Day Card</title><link href="{FONT_URL}" rel="stylesheet">
<style>body{{background:#E9F0EA;margin:0;padding:1.5rem;font-family:sans-serif}}.wrap{{max-width:660px;margin:auto}}
.pdfbtn{{display:block;margin:0 auto 1rem;padding:.6rem 1.4rem;background:#F0B429;color:#1E3B2C;border:2px solid #1E3B2C;
border-radius:8px;font-weight:800;cursor:pointer}}
@media print{{.pdfbtn{{display:none}}body{{background:#fff;padding:0}}*{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}}}
{CARD_CSS}</style></head><body><div class="wrap">
<button class="pdfbtn" onclick="window.print()">Save as PDF</button>{card_html(w)}</div></body></html>"""


def card_pdf(w):
    th = THEMES[w["theme"]]
    _, _, _, body, head, size = FONT_STYLES[w["font"]]
    lt = LANG_TEXT[w["lang"]]
    buf = io.BytesIO()
    W, H = landscape(A4)
    c = canvas.Canvas(buf, pagesize=(W, H))
    m = 28
    c.setFillColor(HexColor("#E9F0EA")); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor(th["frame"])); c.roundRect(m, m, W - 2 * m, H - 2 * m, 6, fill=1, stroke=0)
    c.setFillColor(HexColor(th["bg"])); c.rect(m + 14, m + 14, W - 2 * m - 28, H - 2 * m - 28, fill=1, stroke=0)
    if th["img"] != "none":  # notebook rules
        c.setStrokeColor(HexColor("#D3DDEE")); c.setLineWidth(0.6)
        for yy in range(m + 40, int(H - m - 14), 24):
            c.line(m + 14, yy, W - m - 14, yy)
    c.setStrokeColor(HexColor(th["fg"])); c.setLineWidth(0.8); c.setDash(4, 4)
    c.rect(m + 26, m + 26, W - 2 * m - 52, H - 2 * m - 52, fill=0, stroke=1); c.setDash()

    def centre(txt, y, font, sz, color):
        c.setFont(font, sz); c.setFillColor(HexColor(color)); c.drawCentredString(W / 2, y, txt)

    def para(txt, y, font, sz, color, width, lead):
        c.setFont(font, sz); c.setFillColor(HexColor(color))
        for line in simpleSplit(txt, font, sz, width):
            c.drawCentredString(W / 2, y, line); y -= lead
        return y

    centre(latin(lt["ribbon"]), 505, "Helvetica-Bold", 10, th["accent"])
    centre(latin(lt["head"]), 462, head, 36, th["accent"])
    centre(latin(lt["to"].format(t=w["t"])), 428, body, 19, th["fg"])
    c.setStrokeColor(HexColor(th["fg"])); c.setDash(3, 3); c.line(W / 2 - 150, 412, W / 2 + 150, 412); c.setDash()
    y = para(latin(w["msg"]), 390, body, size, th["fg"], 620, size + 6)
    if w["extra"].strip():
        y = para("P.S. " + latin(w["extra"]), y - 2, body, size - 3, th["fg"], 620, size + 2)

    lines = simpleSplit(latin(w["hadith_text"]), body, 12, 560)
    bh = len(lines) * 15 + 38
    top = y - 6
    c.setFillColor(HexColor(th["soft"])); c.setStrokeColor(HexColor(th["accent"])); c.setLineWidth(1.2)
    c.roundRect(W / 2 - 300, top - bh, 600, bh, 6, fill=1, stroke=1)
    ty = top - 20
    c.setFont(body, 12); c.setFillColor(HexColor(th["fg"]))
    for line in lines:
        c.drawString(W / 2 - 280, ty, line); ty -= 15
    c.setFont("Helvetica-Bold", 9); c.setFillColor(HexColor(th["accent"]))
    c.drawString(W / 2 - 280, ty - 2, "Hadith: " + latin(w["hadith_ref"]))

    c.setFont(head, 18); c.setFillColor(HexColor(th["accent"]))
    c.drawRightString(W - m - 44, 112, "- " + latin(w["student"]))
    if w["school"].strip():
        c.setFont("Helvetica", 10); c.setFillColor(HexColor(th["fg"]))
        c.drawRightString(W - m - 44, 97, latin(w["school"]))
    centre(f"Designed by {DESIGNER}", 66, "Helvetica-Oblique", 9, th["fg"])
    c.showPage(); c.save()
    return buf.getvalue()


# ---------- Page ----------
st.markdown(
    """<div class="hero">
<div class="pill">5 OCTOBER &nbsp;|&nbsp; WORLD TEACHERS' DAY</div>
<h1>Say thank you to your teacher</h1>
<p>Pick a language, a writing style and a card colour. Get a card with a heartfelt message and a hadith on honouring teachers.</p>
</div>""",
    unsafe_allow_html=True,
)

with st.form("wish_form"):
    c1, c2 = st.columns(2)
    student = c1.text_input("Your name", placeholder="e.g. Hamza Ali")
    school = c2.text_input("Class or school (optional)", placeholder="e.g. Class 9, Government High School")
    c3, c4 = st.columns([1, 2])
    honor = c3.selectbox("You call your teacher", list(HONORIFICS))
    teacher = c4.text_input("Teacher's name", placeholder="e.g. Ahmed")
    c5, c6 = st.columns(2)
    lang = c5.radio("Card language", LANGUAGES)
    tone = c6.radio("Message style", list(MESSAGES["English"]))
    c7, c8 = st.columns(2)
    font = c7.selectbox("Writing style", list(FONT_STYLES))
    theme = c8.selectbox("Card colours", list(THEMES))
    extra = st.text_input("Add your own line (optional)", max_chars=140, placeholder="e.g. I will never forget your Friday quizzes")
    go = st.form_submit_button("Create my card", use_container_width=True)

if go:
    if not student.strip() or not teacher.strip():
        st.error("Please enter your name and your teacher's name.")
    else:
        if lang == "Urdu":
            t = f"{HONORIFICS[honor]} {teacher.strip()}".strip()
        else:
            t = teacher.strip() if honor == "Name only" else f"{honor} {teacher.strip()}"
        h = random.choice(HADITHS)
        st.session_state["wish"] = dict(
            student=student, school=school, t=t, lang=lang, font=font, theme=theme, extra=extra,
            msg=random.choice(MESSAGES[lang][tone]).format(t=t),
            hadith_text=h["text"][lang], hadith_ref=h["ref"][lang],
        )
        wall().append({"student": student.strip(), "t": t})
        st.balloons()

w = st.session_state.get("wish")
if w:
    st.markdown(card_html(w), unsafe_allow_html=True)
    st.write("")
    d1, d2, d3 = st.columns(3)
    if w["lang"] == "Urdu":
        d1.download_button("Download card (web page)", card_file(w), "teachers_day_card.html", "text/html", use_container_width=True)
        st.info("For a PDF of an Urdu card: open the downloaded web page and press the Save as PDF button on top.")
    else:
        d1.download_button("Download as PDF", card_pdf(w), "teachers_day_card.pdf", "application/pdf", use_container_width=True)
        d2.download_button("Download as web page", card_file(w), "teachers_day_card.html", "text/html", use_container_width=True)
    d3.button("Make another card", on_click=lambda: st.session_state.pop("wish", None), use_container_width=True)

st.markdown('<div class="wall-title">Wishes so far</div>', unsafe_allow_html=True)
recent = wall()[-12:][::-1]
if not recent:
    st.caption("No wishes yet. Yours can be the first.")
for n in recent:
    st.markdown(f'<div class="note"><b>{esc(n["student"])}</b> thanked {esc(n["t"])}</div>', unsafe_allow_html=True)

st.markdown(f'<div class="credit">Designed by <b>{DESIGNER}</b></div>', unsafe_allow_html=True)
