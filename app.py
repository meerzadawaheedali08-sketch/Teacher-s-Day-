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
STARS = ("radial-gradient(1.5px 1.5px at 20% 30%,#fff 50%,transparent),radial-gradient(1px 1px at 70% 20%,#fff 50%,transparent),"
         "radial-gradient(1.5px 1.5px at 85% 70%,#fff 50%,transparent),radial-gradient(1px 1px at 40% 80%,#fff 50%,transparent),"
         "radial-gradient(1px 1px at 10% 60%,#fff 50%,transparent),radial-gradient(1.5px 1.5px at 55% 45%,#fff 50%,transparent)")
THEMES = {
    "Classic chalkboard": dict(bg="#1E3B2C", fg="#F4F2E8", accent="#F0B429", frame="#8B5E3C", soft="#2B503D", tray="#F4F2E8", img="none"),
    "Pakistan green": dict(bg="#01411C", fg="#FFFFFF", accent="#CFE8D3", frame="#E8F1EA", soft="#0B5A2E", tray="#01411C", img="none"),
    "Midnight and gold": dict(bg="#14213D", fg="#F1F3F8", accent="#E5B84B", frame="#A67C2E", soft="#1F3159", tray="#FFFFFF", img="none"),
    "Maroon and gold": dict(bg="#4A1420", fg="#FBF1E4", accent="#E3B964", frame="#2B0B12", soft="#5E2230", tray="#FBF1E4", img="none"),
    "School notebook": dict(bg="#FBFBF7", fg="#1F2A44", accent="#B5342A", frame="#1F2A44", soft="#EEF1F8", tray="#FFFFFF", img=NOTEBOOK_LINES),
    "Vintage parchment": dict(bg="#EFE0BD", fg="#3E2A18", accent="#9A2E1C", frame="#5C3B1E", soft="#E4D2A8", tray="#F5E9CC", img="none"),
    "Royal purple": dict(bg="#2D1B4E", fg="#F5EEFF", accent="#F5C16C", frame="#C9A24B", soft="#3D2A63", tray="#2D1B4E", img="none"),
    "Ocean teal": dict(bg="#0B3C49", fg="#EAF7F7", accent="#FFD166", frame="#DCEBEC", soft="#145263", tray="#0B3C49", img="none"),
    "Rose garden": dict(bg="#FCE9EE", fg="#5B1F33", accent="#B3174F", frame="#B3174F", soft="#F7D3DD", tray="#FFFFFF", img="none"),
    "Starry night": dict(bg="#0A0F24", fg="#EEF1FF", accent="#FFE08A", frame="#26336B", soft="#141C42", tray="#EEF1FF", img=STARS),
}
HONORIFICS = {"Sir": "سر", "Miss": "مس", "Madam": "میڈم", "Ustad ji": "استاد جی", "Ustani ji": "استانی جی", "Name only": ""}

LANG_TEXT = {
    "English": dict(ribbon="WORLD TEACHERS' DAY  |  5 OCTOBER", head="Happy Teachers' Day!", to="For {t}", ps="P.S.", hl="Hadith:"),
    "Roman Urdu": dict(ribbon="ALAMI YOUM-E-ASATZA  |  5 OCTOBER", head="Teachers' Day Mubarak!", to="{t} ke naam", ps="P.S.", hl="Hadith:"),
    "Urdu": dict(ribbon="عالمی یومِ اساتذہ  |  ۵ اکتوبر", head="عالمی یومِ اساتذہ مبارک", to="{t} کے نام", ps="نوٹ:", hl="حدیث:"),
}

PARTS = {
    "English": {
        "Heartfelt": [
            [
                "Dear {t}, on this World Teachers' Day I want to say what I do not say often enough: thank you.",
                "{t}, some people walk into our lives and quietly change the direction of our future. For me, that person is you.",
                "Respected {t}, today I am not thinking about exams or marks, only about everything you have done for me.",
                "To my dear teacher {t}: thank you for being the first person who made me believe I could do more.",
                "Dear {t}, a teacher's work is never really finished, and neither is our gratitude, so I am saying it again today.",
            ],
            [
                "You taught us the lesson in the book and, far more importantly, the lesson of patience, honesty and hard work.",
                "You never gave up on me, even on the days when I had given up on myself, and that has stayed with me.",
                "Every correction you made came with care, and I understand now that your strictness was only your way of loving us.",
                "You stayed back after the bell, explained the same thing again and again, and never once made me feel small.",
                "Because of you, I stopped being afraid of asking questions, and that changed the way I learn and the way I think.",
                "The values you showed us in the classroom, kindness, discipline and respect, are things no exam can measure.",
                "Whatever I become in life, a little part of your effort and your duas will always be in it.",
            ],
            [
                "May Allah reward you for every child you have guided, and keep you healthy, respected and happy always.",
                "I promise to make you proud, and to pass on what you gave me to others. Happy Teachers' Day!",
                "You will always have my respect and my duas. Happy World Teachers' Day, and thank you for everything.",
                "Thank you for lighting the way. Wishing you a day as bright as the future you helped us build.",
                "With love, respect and endless gratitude, I wish you a very happy Teachers' Day.",
            ],
        ],
        "Funny": [
            [
                "Dear {t}, I have been planning this message for days, mostly because I could not find a way to say thank you without sounding like I am asking for extra marks.",
                "{t}, breaking news: your students have finally noticed that you were right all along.",
                "Dear {t}, the whole class asked me to write this, and by the whole class I mean me, because everyone else was busy copying homework.",
                "Respected {t}, on Teachers' Day we promise to be good students for at least the next twenty-four hours.",
            ],
            [
                "Thank you for staying calm when we said the dog ate our notebook, the van was late and the internet was down, all in one week.",
                "Thank you for pretending not to notice the whispering at the back, and for knowing exactly when to turn around.",
                "You somehow make even the most boring chapter bearable, and that is a talent no textbook can teach.",
                "Your red pen has seen things, and yet you still smile when you hand back our copies.",
                "You explained the same topic five times without sighing even once, which honestly deserves an award.",
                "You know every excuse in the book and still give us another chance, so we think you might be a superhero.",
            ],
            [
                "Class would be incomplete without you. Happy Teachers' Day, and please keep the surprise tests to a minimum.",
                "We promise to listen more, talk less and write neater. Happy World Teachers' Day!",
                "Thank you for everything, and for not reading too much into our handwriting. Happy Teachers' Day!",
                "Stay awesome, stay strict only when needed, and have a wonderful Teachers' Day!",
            ],
        ],
    },
    "Roman Urdu": {
        "Heartfelt": [
            [
                "Respected {t}, World Teachers' Day par dil ki ek hi baat hai: shukriya, bohat bohat shukriya.",
                "{t}, kuch log zindagi mein aate hain aur khamoshi se hamara mustaqbil badal dete hain. Mere liye woh aap hain.",
                "Dear {t}, aaj exams ya marks ki nahi, sirf un sab meharbaniyon ki baat hai jo aap ne mujh par ki.",
                "Mohtaram {t}, aap ne sab se pehle mujhe yaqeen dilaya ke mujh mein bohat kuch karne ki salahiyat hai.",
            ],
            [
                "Aap ne kitab ka sabaq to parhaya hi, magar us se bhi zyada sabr, imaandari aur mehnat ka sabaq sikhaya.",
                "Jin dinon mein mujhe khud par bharosa nahi raha, un dinon mein bhi aap ne mujh par yaqeen rakha.",
                "Aap ki har tokne mein fikr thi, aur ab samajh aaya ke aap ki sakhti dar asal aap ki mohabbat thi.",
                "Chhutti ke baad ruk kar, ek hi baat baar baar samjha kar, aap ne kabhi mujhe chhota mehsoos nahi hone diya.",
                "Aap ki wajah se sawal poochne ka darr khatam hua, aur isi ne meri sochne aur seekhne ki rah badal di.",
                "Main jo bhi banoon, us mein aap ki mehnat aur aap ki duaon ka ek hissa hamesha shamil hoga.",
            ],
            [
                "Allah aap ko har us bachche ke badle ajar de jis ki aap ne rehnumai ki, aur aap ko sehat, izzat aur khushiyan ata farmaye.",
                "Wada hai ke aap ko fakhar ka mauqa deta rahoon aur jo aap se paaya woh doosron tak pohanchata rahoon. Teachers' Day mubarak!",
                "Aap ke liye hamesha izzat aur duain. World Teachers' Day mubarak, aur har cheez ka shukriya.",
                "Mohabbat, izzat aur be-intiha shukriye ke saath, aap ko Teachers' Day bohat bohat mubarak ho.",
            ],
        ],
        "Funny": [
            [
                "Dear {t}, kai din se yeh message likhne ka soch rahe thay, kyun ke extra marks maangay baghair shukriya kehna bohat mushkil hai.",
                "{t}, breaking news: aap ke students ko aakhir maloom ho gaya ke aap hamesha sahi thay.",
                "Respected {t}, poori class ne yeh likhwaya hai, aur poori class se meri murad main hoon, kyun ke baaqi sab homework copy karne mein masroof thay.",
            ],
            [
                "Shukriya jab hum ne kaha ke kutte ne copy kha li, van late thi aur internet band tha, woh bhi ek hi hafte mein, aur aap phir bhi pur-sukoon rahe.",
                "Shukriya ke aap ne piche ki seat par hone wali sargoshiyon ko nazar-andaz kiya, aur hamesha theek waqt par palat kar dekha.",
                "Sab se boring chapter ko bhi aap bardasht ke qabil bana dete hain, aur yeh woh hunar hai jo kisi kitab mein nahi milta.",
                "Aap ne ek hi topic panch baar samjhaya aur ek baar bhi aah nahi bhari, is par to inaam banta hai.",
                "Aap hamari har bahane-baazi jaante hain, phir bhi doosra mauqa dete hain, lagta hai aap superhero hain.",
            ],
            [
                "Aap ke baghair class adhoori hai. Teachers' Day mubarak, bas surprise test zara kam rakhiye ga.",
                "Wada hai ke zyada sunein ge, kam bolein ge aur likhai saaf karein ge. World Teachers' Day mubarak!",
                "Hamesha aise hi kamaal rahiye. Aap ko Teachers' Day bohat mubarak!",
            ],
        ],
    },
    "Urdu": {
        "Heartfelt": [
            [
                "محترم {t}، عالمی یومِ اساتذہ پر دل کی بس ایک ہی بات ہے: شکریہ، بہت بہت شکریہ۔",
                "{t}، کچھ لوگ خاموشی سے ہماری زندگی کا رخ بدل دیتے ہیں۔ میرے لیے وہ آپ ہیں۔",
                "محترم {t}، آج امتحانوں اور نمبروں کی نہیں، ان تمام مہربانیوں کی بات ہے جو آپ نے مجھ پر کیں۔",
                "{t}، آپ ہی نے سب سے پہلے مجھے یقین دلایا کہ مجھ میں بہت کچھ کرنے کی صلاحیت ہے۔",
            ],
            [
                "آپ نے کتاب کا سبق تو پڑھایا ہی، مگر اس سے بڑھ کر صبر، ایمانداری اور محنت کا سبق سکھایا۔",
                "جن دنوں مجھے خود پر بھروسا نہ رہا، ان دنوں میں بھی آپ نے مجھ پر یقین رکھا۔",
                "آپ کی ہر ٹوک میں فکر تھی، اور اب سمجھ آیا کہ آپ کی سختی دراصل آپ کی محبت تھی۔",
                "آپ کی وجہ سے سوال پوچھنے کا ڈر ختم ہوا، اور اسی نے میرے سیکھنے کا انداز بدل دیا۔",
                "میں زندگی میں جو کچھ بھی بنوں، اس میں آپ کی محنت اور دعاؤں کا ایک حصہ ہمیشہ شامل رہے گا۔",
            ],
            [
                "اللہ آپ کو ہر اس بچے کے بدلے اجر دے جس کی آپ نے رہنمائی کی، اور آپ کو صحت، عزت اور خوشیاں عطا فرمائے۔",
                "وعدہ ہے کہ آپ کی دی ہوئی تعلیم دوسروں تک پہنچانے کی پوری کوشش رہے گی۔ یومِ اساتذہ مبارک!",
                "آپ کے لیے ہمیشہ عزت اور دعائیں۔ عالمی یومِ اساتذہ مبارک، اور ہر بات کا شکریہ۔",
                "محبت، عزت اور بے پناہ شکرگزاری کے ساتھ، آپ کو یومِ اساتذہ بہت بہت مبارک ہو۔",
            ],
        ],
        "Funny": [
            [
                "محترم {t}، کئی دن سے یہ پیغام لکھنے کا سوچ رہے تھے، کیونکہ اضافی نمبر مانگے بغیر شکریہ کہنا بہت مشکل ہے۔",
                "{t}، بریکنگ نیوز: آپ کے شاگردوں کو آخرکار معلوم ہو گیا کہ آپ ہمیشہ ٹھیک تھے۔",
                "محترم {t}، پوری کلاس نے یہ لکھوایا ہے، اور پوری کلاس سے مراد میں ہوں، کیونکہ باقی سب ہوم ورک کاپی کرنے میں مصروف تھے۔",
            ],
            [
                "شکریہ کہ جب ہم نے کہا کاپی کتے نے کھا لی، وین لیٹ تھی اور انٹرنیٹ بند تھا، وہ بھی ایک ہی ہفتے میں، تب بھی آپ پرسکون رہے۔",
                "سب سے بور باب کو بھی آپ قابلِ برداشت بنا دیتے ہیں، اور یہ وہ ہنر ہے جو کسی کتاب میں نہیں ملتا۔",
                "آپ نے ایک ہی ٹاپک پانچ بار سمجھایا اور ایک بار بھی آہ نہیں بھری، اس پر تو انعام بنتا ہے۔",
                "آپ ہماری ہر بہانہ بازی جانتے ہیں، پھر بھی دوسرا موقع دیتے ہیں، لگتا ہے آپ سپر ہیرو ہیں۔",
            ],
            [
                "آپ کے بغیر کلاس ادھوری ہے۔ یومِ اساتذہ مبارک، بس سرپرائز ٹیسٹ ذرا کم رکھیے گا۔",
                "وعدہ ہے کہ زیادہ سنیں گے، کم بولیں گے اور لکھائی صاف کریں گے۔ عالمی یومِ اساتذہ مبارک!",
                "ہمیشہ ایسے ہی کمال رہیے۔ آپ کو یومِ اساتذہ بہت مبارک!",
            ],
        ],
    },
}

SHORT = {
    "English": [
        "Some people teach lessons, you taught life. Thank you, {t}. Happy Teachers' Day!",
        "A good teacher lights a thousand candles without losing a single flame. Thank you, {t}!",
        "Thank you, {t}, for turning confusion into confidence. Happy Teachers' Day!",
        "{t}, your words are still guiding me long after the class has ended. Thank you.",
        "To the one who believed in me first: thank you, {t}. Happy World Teachers' Day!",
        "Every success of mine has your signature on it, {t}. Happy Teachers' Day!",
        "Dear {t}, you are the reason I love learning. Thank you from the heart.",
        "{t}, a teacher plants a seed and never knows where the forest ends. Thank you for planting me.",
        "Respect and gratitude to you, {t}, today and always.",
        "Happy Teachers' Day, {t}! You make the world better, one student at a time.",
    ],
    "Roman Urdu": [
        "Jo chiragh ban kar jalte hain, wohi ustad kehlate hain. {t}, aap ko Teachers' Day mubarak!",
        "{t}, aap ne uljhan ko aitemaad mein badal diya. Shukriya aur Teachers' Day mubarak!",
        "{t}, class khatam ho gayi magar aap ki baatein aaj bhi rasta dikhati hain. Shukriya.",
        "Jis ne sab se pehle mujh par yaqeen kiya, us ke naam: shukriya {t}. Teachers' Day mubarak!",
        "Meri har kamyabi par aap ke dastkhat hain, {t}. Teachers' Day mubarak!",
        "{t}, aap ki wajah se mujhe parhna acha lagta hai. Dil se shukriya.",
        "{t}, ustad ek beej bota hai aur nahi jaanta ke jungle kahan tak jaye ga. Mujhe bone ka shukriya.",
        "{t}, aap ke liye aaj aur hamesha izzat aur shukriya.",
    ],
    "Urdu": [
        "جو چراغ بن کر جلتے ہیں، وہی استاد کہلاتے ہیں۔ {t}، آپ کو یومِ اساتذہ مبارک!",
        "{t}، آپ نے الجھن کو اعتماد میں بدل دیا۔ شکریہ اور یومِ اساتذہ مبارک!",
        "{t}، کلاس ختم ہو گئی مگر آپ کی باتیں آج بھی راستہ دکھاتی ہیں۔ شکریہ۔",
        "جس نے سب سے پہلے مجھ پر یقین کیا، اس کے نام: شکریہ {t}۔ یومِ اساتذہ مبارک!",
        "میری ہر کامیابی پر آپ کے دستخط ہیں، {t}۔ یومِ اساتذہ مبارک!",
        "{t}، آپ کی وجہ سے مجھے پڑھنا اچھا لگتا ہے۔ دل سے شکریہ۔",
        "{t}، استاد ایک بیج بوتا ہے اور نہیں جانتا کہ جنگل کہاں تک جائے گا۔ مجھے بونے کا شکریہ۔",
    ],
}
TONES = ["Heartfelt", "Funny", "Short and sweet"]


def compose(lang, tone, t):
    """Builds a fresh wish: opening + middle + closing (hundreds of combinations)."""
    if tone == "Short and sweet":
        return random.choice(SHORT[lang]).format(t=t)
    return " ".join(random.choice(part) for part in PARTS[lang][tone]).format(t=t)


def reroll():
    w = st.session_state.get("wish")
    if not w:
        return
    for _ in range(10):
        m = compose(w["lang"], w["tone"], w["t"])
        if m != w["msg"]:
            break
    w["msg"] = m


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
.board{transform-origin:top center;transform:rotate(-.6deg);animation:drop 1.2s cubic-bezier(.2,.8,.3,1) both}
.board::after{content:"";position:absolute;inset:0;pointer-events:none;opacity:.13;mix-blend-mode:multiply;
  background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>")}
.board .tape{position:absolute;top:10px;width:110px;height:26px;z-index:2;background:rgba(255,226,140,.8);
  box-shadow:0 1px 3px rgba(0,0,0,.3)}
.board .tape.l{left:-34px;transform:rotate(-40deg)}
.board .tape.r{right:-34px;transform:rotate(40deg)}
.board .star span{display:inline-block;animation:tw 2.6s ease-in-out infinite}
.board .star span:nth-child(2){animation-delay:.5s;font-size:1.5em}
.board .star span:nth-child(3){animation-delay:1s}
.board .head,.board .to,.board .msg,.board .ps,.board .hadith,.board .from{animation:ink .9s ease both}
.board .head{animation-delay:.9s}.board .to{animation-delay:1.3s}.board .msg{animation-delay:1.7s}
.board .ps{animation-delay:2.2s}.board .hadith{animation-delay:2.6s}.board .from{animation-delay:3.1s}
@keyframes drop{0%{opacity:0;transform:translateY(-60px) rotate(-5deg)}55%{opacity:1;transform:translateY(8px) rotate(1.6deg)}
  78%{transform:translateY(-2px) rotate(-1.2deg)}100%{opacity:1;transform:translateY(0) rotate(-.6deg)}}
@keyframes ink{from{opacity:0;filter:blur(3px);transform:translateY(8px)}to{opacity:1;filter:none;transform:none}}
@keyframes tw{0%,100%{opacity:.35;transform:scale(.8)}50%{opacity:1;transform:scale(1.15)}}
@media (prefers-reduced-motion:reduce){.board,.board *{animation:none!important}}
@media print{.board,.board *{animation:none!important}.board{transform:none;box-shadow:none}}
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
  <i class="tape l"></i><i class="tape r"></i>
  <span class="ribbon">{lt['ribbon']}</span>
  <div class="star"><span>&#9733;</span><span>&#9733;</span><span>&#9733;</span></div>
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
    if th["img"] == NOTEBOOK_LINES:  # notebook rules
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
    tone = c6.radio("Message style", TONES)
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
            msg=compose(lang, tone, t), tone=tone,
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
    st.button("Write a different wish", on_click=reroll, use_container_width=True)

st.markdown('<div class="wall-title">Wishes so far</div>', unsafe_allow_html=True)
recent = wall()[-12:][::-1]
if not recent:
    st.caption("No wishes yet. Yours can be the first.")
for n in recent:
    st.markdown(f'<div class="note"><b>{esc(n["student"])}</b> thanked {esc(n["t"])}</div>', unsafe_allow_html=True)

st.markdown(f'<div class="credit">Designed by <b>{DESIGNER}</b></div>', unsafe_allow_html=True)
