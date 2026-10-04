import html
import random
import urllib.parse

import streamlit as st

st.set_page_config(page_title="Ustad ke naam | یومِ اساتذہ", page_icon="🍎", layout="centered")

FONTS = (
    "https://fonts.googleapis.com/css2?family=Caveat:wght@600;700"
    "&family=Nunito:wght@400;600;800&family=Noto+Nastaliq+Urdu:wght@400;600&display=swap"
)

# ---------- Styles ----------
CARD_CSS = """
.board{background:#1E3B2C;color:#F4F2E8;border:12px solid #8B5E3C;border-radius:6px;
  padding:2rem 1.5rem 1.4rem;box-shadow:inset 0 0 50px rgba(0,0,0,.4);text-align:center}
.board .head{font-family:'Caveat',cursive;font-size:2.5rem;color:#F0B429;line-height:1.1}
.board .head.urdu{font-family:'Noto Nastaliq Urdu',serif;font-size:1.7rem;line-height:2}
.board .to{font-family:'Caveat',cursive;font-size:1.9rem;margin-top:.6rem}
.board .to.urdu{font-family:'Noto Nastaliq Urdu',serif;font-size:1.3rem;line-height:2}
.board hr{border:0;border-top:2px dashed rgba(244,242,232,.35);margin:.9rem auto;width:70%}
.board .msg{font-family:'Caveat',cursive;font-size:1.6rem;line-height:1.45;max-width:34rem;margin:.6rem auto}
.board .msg.urdu{font-family:'Noto Nastaliq Urdu',serif;font-size:1.15rem;line-height:2.5;direction:rtl}
.board .ps{font-family:'Caveat',cursive;font-size:1.35rem;opacity:.85;margin-top:.4rem}
.board .from{font-family:'Caveat',cursive;font-size:1.7rem;color:#F0B429;text-align:right;margin-top:1rem}
.board .from small{display:block;font-size:1.15rem;color:#F4F2E8;opacity:.8}
"""

PAGE_CSS = f"""
@import url('{FONTS}');
html, body, [class*="css"], .stApp {{ font-family:'Nunito',sans-serif; }}
.stApp {{ background:#E9F0EA; }}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ max-width:760px; padding-top:2rem; }}
.hero {{ text-align:center; margin-bottom:1.2rem; }}
.hero h1 {{ font-family:'Caveat',cursive; font-size:3.4rem; color:#1E3B2C; margin:0; line-height:1; }}
.hero .ur {{ font-family:'Noto Nastaliq Urdu',serif; font-size:1.5rem; color:#8B5E3C; margin-top:.4rem; line-height:2; }}
.hero p {{ color:#3d5246; margin:.2rem 0 0; }}
div[data-testid="stForm"] {{ background:#fff; border:2px solid #1E3B2C; border-radius:10px; padding:1.2rem 1.4rem; }}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button, .stLinkButton > a {{
  background:#F0B429; color:#1E3B2C; border:2px solid #1E3B2C; border-radius:8px; font-weight:800; }}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover {{
  background:#1E3B2C; color:#F0B429; border-color:#1E3B2C; }}
.wall-title {{ font-family:'Caveat',cursive; font-size:2rem; color:#1E3B2C; margin:1.6rem 0 .4rem; }}
.note {{ background:#fff; border-left:6px solid #F0B429; border-radius:6px; padding:.6rem .9rem; margin-bottom:.5rem; color:#26382e; }}
.note b {{ color:#1E3B2C; }}
{CARD_CSS}
"""
st.markdown(f"<style>{PAGE_CSS}</style>", unsafe_allow_html=True)

# ---------- Content ----------
HONORIFICS = {
    "Sir": "سر", "Miss": "مس", "Madam": "میڈم",
    "Ustad ji": "استاد جی", "Ustani ji": "استانی جی", "Sirf naam": "",
}

# {t} = teacher ka naam (honorific ke saath)
MESSAGES = {
    "Urdu": {
        "Dil se": [
            "محترم {t}، آپ کی محنت، صبر اور رہنمائی نے مجھے سکھایا کہ علم صرف کتابوں میں نہیں، کردار میں بھی ہوتا ہے۔ آج میں جو کچھ ہوں، آپ کی تربیت اور دعاؤں کا نتیجہ ہے۔ عالمی یومِ اساتذہ مبارک!",
            "{t}، آپ نے ہمیں صرف پڑھایا نہیں، جینا بھی سکھایا۔ اللہ آپ کو صحت، عزت اور ڈھیروں خوشیاں عطا فرمائے۔ یومِ اساتذہ مبارک!",
        ],
        "Mazahiya": [
            "محترم {t}، ہوم ورک کم دینے کی گزارش اپنی جگہ، مگر سچ یہ ہے کہ آپ کے بغیر ہماری کلاس ادھوری ہے۔ یومِ اساتذہ مبارک!",
        ],
        "Chhota aur pyara": [
            "جو چراغ بن کر جلتے ہیں، وہی استاد کہلاتے ہیں۔ {t}، آپ کو یومِ اساتذہ مبارک!",
        ],
    },
    "Roman Urdu": {
        "Dil se": [
            "Respected {t}, aap ne sirf parhaya nahi, zindagi jeena bhi sikhaya. Aap ki mehnat, sabr aur duaon ki wajah se aaj main apne khwab dekhne ke qabil hoon. Allah aap ko sehat aur khushiyan de. Happy Teachers' Day!",
            "{t}, aap ka diya hua ilm hamari zindagi ki sab se bari daulat hai. Shukriya har sabaq ke liye, aur un sab dantoon ke liye jo humare bhale ke liye thin. Teachers' Day mubarak!",
        ],
        "Mazahiya": [
            "Respected {t}, homework kam dene ki darkhwast apni jagah, magar sach yeh hai ke aap ke baghair hamari class adhoori hai. Teachers' Day mubarak!",
            "{t}, aap ki class mein sab se mushkil kaam hai, sawal ka jawab na aane par bhi muskurana. Aap ko Teachers' Day mubarak!",
        ],
        "Chhota aur pyara": [
            "Jo chiragh ban kar jalte hain, wohi ustad kehlate hain. {t}, aap ko Teachers' Day mubarak!",
        ],
    },
    "English": {
        "Dil se": [
            "Dear {t}, thank you for teaching me not just lessons, but patience, honesty and self-belief. Everything I achieve will carry a little of your effort. Happy World Teachers' Day!",
        ],
        "Mazahiya": [
            "Dear {t}, thank you for believing in us even when we forgot our homework (again). Class would be incomplete without you. Happy Teachers' Day!",
        ],
        "Chhota aur pyara": [
            "Some people teach lessons, you taught life. Thank you, {t}. Happy Teachers' Day!",
        ],
    },
}

HEADS = {"Urdu": "عالمی یومِ اساتذہ مبارک", "Roman Urdu": "Teachers' Day Mubarak!", "English": "Happy Teachers' Day!"}
TO_LINE = {"Urdu": "{t} کے نام", "Roman Urdu": "{t} ke naam", "English": "For {t}"}


@st.cache_resource
def wall():
    """Server chalne tak sab users ki wishes yahan rehti hain."""
    return []


def esc(s):
    return html.escape(s.strip())


def card_html(w):
    urdu = " urdu" if w["lang"] == "Urdu" else ""
    ps = f'<div class="ps">P.S. {esc(w["extra"])}</div>' if w["extra"] else ""
    sub = f"<small>{esc(w['school'])}</small>" if w["school"] else ""
    subj = f" · {esc(w['subject'])}" if w["subject"] else ""
    return f"""
<div class="board">
  <div class="head{urdu}">{HEADS[w['lang']]}</div>
  <div class="to{urdu}">{TO_LINE[w['lang']].format(t=esc(w['t']))}{subj}</div>
  <hr>
  <div class="msg{urdu}">{esc(w['msg'])}</div>
  {ps}
  <div class="from">— {esc(w['student'])}{sub}</div>
</div>"""


def card_file(w):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Teachers' Day Wish</title>
<link href="{FONTS}" rel="stylesheet">
<style>body{{background:#E9F0EA;margin:0;padding:1.5rem;font-family:sans-serif}}
.wrap{{max-width:640px;margin:auto}}{CARD_CSS}</style></head>
<body><div class="wrap">{card_html(w)}</div></body></html>"""


def plain_text(w):
    t = w["msg"] + (f"\n\nP.S. {w['extra'].strip()}" if w["extra"] else "")
    return f"{t}\n\n— {w['student'].strip()}" + (f", {w['school'].strip()}" if w["school"] else "")


# ---------- Page ----------
st.markdown(
    """<div class="hero">
<h1>Ustad ke naam ek wish</h1>
<div class="ur">اپنے استاد کو شکریہ کہیے</div>
<p>5 October, World Teachers' Day. Naam likho, message chuno, card tayyar.</p>
</div>""",
    unsafe_allow_html=True,
)

with st.form("wish_form"):
    c1, c2 = st.columns(2)
    student = c1.text_input("Aap ka naam", placeholder="e.g. Hamza Ali")
    school = c2.text_input("Class / School (optional)", placeholder="e.g. Class 9, Beaconhouse")
    c3, c4 = st.columns([1, 2])
    honor = c3.selectbox("Teacher ko kya kehte hain?", list(HONORIFICS))
    teacher = c4.text_input("Teacher ka naam", placeholder="e.g. Ahmed / Sara")
    subject = st.text_input("Subject (optional)", placeholder="e.g. Maths, Urdu, Physics")
    c5, c6 = st.columns(2)
    lang = c5.radio("Zubaan", list(MESSAGES), horizontal=True)
    tone = c6.radio("Andaaz", list(MESSAGES["English"]), horizontal=True)
    extra = st.text_input("Apni taraf se ek line (optional)", max_chars=140)
    go = st.form_submit_button("Wish tayyar karo", use_container_width=True)

if go:
    if not student.strip() or not teacher.strip():
        st.error("Apna naam aur teacher ka naam zaroor likho.")
    else:
        prefix = HONORIFICS[honor] if lang == "Urdu" else ("" if honor == "Sirf naam" else honor)
        t = f"{prefix} {teacher.strip()}".strip()
        msg = random.choice(MESSAGES[lang][tone]).format(t=t)
        st.session_state["wish"] = dict(
            student=student, school=school, t=t, subject=subject,
            lang=lang, msg=msg, extra=extra,
        )
        wall().append({"student": student.strip(), "t": t, "msg": msg})
        st.balloons()

w = st.session_state.get("wish")
if w:
    st.markdown(card_html(w), unsafe_allow_html=True)
    st.write("")
    d1, d2, d3 = st.columns(3)
    d1.download_button("Card download (.html)", card_file(w), "teachers_day_card.html", "text/html", use_container_width=True)
    d2.download_button("Text download (.txt)", plain_text(w), "teachers_day_wish.txt", use_container_width=True)
    d3.link_button("WhatsApp par bhejo", "https://wa.me/?text=" + urllib.parse.quote(plain_text(w)), use_container_width=True)

st.markdown('<div class="wall-title">Sab ki wishes</div>', unsafe_allow_html=True)
recent = wall()[-12:][::-1]
if not recent:
    st.caption("Abhi koi wish nahi aayi. Pehli wish aap ki ho sakti hai.")
for n in recent:
    st.markdown(
        f'<div class="note"><b>{esc(n["student"])}</b> ne {esc(n["t"])} ko wish kiya</div>',
        unsafe_allow_html=True,
    )
