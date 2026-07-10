from flask import Flask, render_template_string, request, make_response, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json, os, datetime, threading, time
import requests

app = Flask(__name__)
app.secret_key = 'super_secret_key_game_master_2026'

BOOKINGS_FILE = 'bookings.json'
COMMENTS_FILE = 'comments.json'
USERS_FILE = 'users.json'
PRICE = 40  

TELEGRAM_TOKEN = "8801743115:AAGN2S0DwR5lSMwYMjmsxLyD4E8LJ62mdZI"
ADMIN_CHAT_ID = "7728398907"

BAD_WORDS = ["شتم", "كلب", "حمار", "غبي", "يا ابن", "عرص", "خول", "شرموط", "تفه", "كس", "زب", "منيك", "قذر", "وسخ"]

def load_users():
    if os.path.exists(USERS_FILE):
        try: return json.load(open(USERS_FILE, encoding='utf-8'))
        except: return {}
    return {}

def save_users(data):
    json.dump(data, open(USERS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        try: return json.load(open(BOOKINGS_FILE, encoding='utf-8'))
        except: return []
    return []

def save_bookings(data):
    json.dump(data, open(BOOKINGS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        try: return json.load(open(COMMENTS_FILE, encoding='utf-8'))
        except: return []
    return [
        {"id": "1", "name": "سارة أحمد", "rating": "5", "text": "مستر ممتاز جداً والرياضيات بقت أسهل مادة عندي بفضله", "date": "2026-07-10"},
        {"id": "2", "name": "محمد كريم", "rating": "4", "text": "أفضل كبسولات ليلة امتحان ممكن تاخدها في حياتك", "date": "2026-07-11"}
    ]

def save_comments(data):
    json.dump(data, open(COMMENTS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def check_profanity(text):
    for word in BAD_WORDS:
        if word in text.lower(): return True
    return False

def send_telegram(msg, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try: return requests.post(url, data=data, timeout=10).json()
    except: return None

HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>سيد اللعبة - مستر الرياضيات</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
:root{--gold:#FFD700;--dark:#0b0c10;--card:#1f2833;--text:#c5c6c7;--teal:#66fcf1}
*{margin:0;padding:0;font-family:'Cairo',sans-serif;box-sizing:border-box;scroll-behavior:smooth}
body{background:var(--dark);color:#fff;overflow-x:hidden}

@keyframes float {0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes glow {0%,100%{box-shadow:0 0 15px var(--gold)}50%{box-shadow:0 0 35px var(--gold)}}
@keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulseGlow {0%{box-shadow: 0 0 10px rgba(255,215,0,0.4); transform: scale(1);} 50%{box-shadow: 0 0 30px var(--gold); transform: scale(1.03);} 100%{box-shadow: 0 0 10px rgba(255,215,0,0.4); transform: scale(1);}}

nav{position:fixed;top:0;width:100%;background:rgba(11, 12, 16, 0.95);backdrop-filter:blur(12px);padding:15px 5%;display:flex;justify-content:space-between;align-items:center;z-index:100;box-shadow:0 4px 20px rgba(0,0,0,0.6);border-bottom:1px solid rgba(255,215,0,0.1)}
nav .logo{font-weight:900;color:var(--gold);font-size:22px;display:flex;align-items:center;gap:10px;text-shadow:0 0 10px rgba(255,215,0,0.3)}
nav .links{display:flex;gap:15px;align-items:center;flex-wrap:wrap}
nav a{color:#fff;text-decoration:none;font-weight:700;transition:0.3s;font-size:14px;white-space:nowrap}
nav a:hover{color:var(--gold)}

.nav-auth-btn{background:transparent;border:2px solid var(--gold);color:var(--gold);padding:6px 18px;border-radius:20px;cursor:pointer;font-weight:700;font-size:13px;transition:0.3s;display:flex;align-items:center;gap:8px;white-space:nowrap}
.nav-auth-btn:hover{background:var(--gold);color:#000;box-shadow:0 0 15px var(--gold)}
.user-badge{background:var(--card);border:1px solid #2f3b4c;color:#fff;padding:6px 15px;border-radius:20px;font-size:13px;font-weight:700;display:flex;align-items:center;gap:8px;white-space:nowrap}
.logout-link{color:#ff4d4d;text-decoration:none;font-size:12px;font-weight:bold;margin-right:8px}
.logout-link:hover{text-decoration:underline}

.hero{min-height:100vh;background:linear-gradient(rgba(11,12,16,0.75),rgba(11,12,16,0.95)),url('https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=2070') center/cover fixed; display:flex;align-items:center;justify-content:center;text-align:center;padding:140px 20px 60px 20px}
.hero-content{animation:fadeIn 1s ease; max-width:800px}
.hero h1{font-size:4rem;font-weight:900;color:var(--gold);margin-bottom:20px;text-shadow:0 0 25px rgba(255,215,0,0.5)}
.hero p{font-size:1.3rem;color:var(--text);margin-bottom:35px;line-height:1.8}
.btn{background:linear-gradient(45deg, var(--gold), #ffb700);color:#000;padding:14px 40px;border:none;border-radius:50px;font-size:18px;font-weight:900;cursor:pointer;transition:0.4s;text-decoration:none;display:inline-block;box-shadow:0 5px 15px rgba(255,215,0,0.3)}
.btn:hover{transform:scale(1.05);box-shadow:0 0 35px var(--gold)}

section{padding:80px 5%;max-width:1300px;margin:auto}
.section-title{text-align:center;font-size:2.5rem;margin-bottom:50px;color:var(--gold);position:relative}
.section-title::after{content:'';position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);width:60px;height:3px;background:var(--gold);border-radius:2px}

.stats-container {display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; text-align: center; margin-bottom: 40px;}
.stat-card {background: var(--card); padding: 30px 20px; border-radius: 18px; border: 1px solid #2f3b4c; border-top: 3px solid var(--gold); transition: 0.3s;}
.stat-card:hover {transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.4);}
.stat-card i {font-size: 2.5rem; color: var(--gold); margin-bottom: 15px;}
.stat-number {font-size: 2rem; font-weight: 900; color: #fff; margin-bottom: 5px;}
.stat-label {color: var(--text); font-size: 14px; font-weight: 700;}

.about{display:flex;gap:50px;align-items:center;flex-wrap:wrap;justify-content:center}
.about img{width:100%;max-width:450px;height:300px;object-fit:cover;border-radius:20px;animation:float 4s ease-in-out infinite, glow 3s ease-in-out infinite;border:3px solid var(--gold)}
.about-text{flex:1;min-width:300px;font-size:1.15rem;line-height:2;color:var(--text)}

.grid-features {display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-top: 20px;}
.feat-box {background: var(--card); border: 2px solid #2f3b4c; padding: 30px 20px; border-radius: 20px; text-align: center; transition: 0.4s;}
.feat-box:hover {border-color: var(--gold); transform: scale(1.03); box-width: 0 10px 30px rgba(255,215,0,0.15);}
.feat-box i {font-size: 3rem; color: var(--gold); margin-bottom: 20px; text-shadow: 0 0 10px rgba(255,215,0,0.3);}
.feat-box h3 {font-size: 1.4rem; color: #fff; margin-bottom: 12px; font-weight: 700;}
.feat-box p {color: var(--text); font-size: 0.95rem; line-height: 1.7;}

.pricing-grid {display: flex; justify-content: center; margin-top: 20px;}
.price-card {background: linear-gradient(145deg, #1f2833, #11161d); border: 2px solid var(--gold); padding: 40px 30px; border-radius: 24px; text-align: center; max-width: 400px; width: 100%; box-shadow: 0 15px 35px rgba(0,0,0,0.5); position: relative; overflow: hidden;}
.price-card::before {content: 'متاح الآن'; position: absolute; top: 20px; right: -35px; background: var(--gold); color: #000; padding: 5px 40px; font-weight: 900; font-size: 12px; transform: rotate(45deg);}
.price-card h3 {font-size: 1.8rem; margin-bottom: 15px; color: #fff;}
.price-amount {font-size: 3.5rem; font-weight: 900; color: var(--gold); margin-bottom: 5px; text-shadow: 0 0 20px rgba(255,215,0,0.4);}
.price-period {color: var(--text); font-size: 14px; margin-bottom: 30px; display: block;}
.price-features {list-style: none; text-align: right; margin-bottom: 35px;}
.price-features li {margin-bottom: 15px; font-weight: 600; font-size: 15px; display: flex; align-items: center; gap: 10px;}
.price-features li i {color: var(--gold);}

.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}
.gallery img{width:100%;height:240px;object-fit:cover;border-radius:15px;transition:0.4s;border:2px solid #333}
.gallery img:hover{transform:scale(1.05) translateY(-5px);border-color:var(--gold);box-shadow:0 10px 25px rgba(255,215,0,0.3)}

.faq-container {max-width: 800px; margin: auto; display: flex; flex-direction: column; gap: 15px;}
.faq-item {background: var(--card); border: 1px solid #2f3b4c; border-radius: 12px; overflow: hidden; transition: 0.3s;}
.faq-btn {width: 100%; background: transparent; border: none; padding: 20px; text-align: right; color: #fff; font-size: 16px; font-weight: 700; cursor: pointer; display: flex; justify-content: space-between; align-items: center; outline: none;}
.faq-btn:hover {color: var(--gold);}
.faq-content {max-height: 0; overflow: hidden; transition: max-height 0.3s ease; background: #151c24; padding: 0 20px; color: var(--text); font-size: 15px; line-height: 1.8;}

.comments-section {background: rgba(31, 40, 51, 0.3); padding: 40px 20px; border-radius: 20px; border: 1px solid #2f3b4c; margin-top: 30px;}
.comments-list {max-height: 400px; overflow-y: auto; margin-bottom: 30px; padding-right: 10px;}
.comment-item {background: var(--card); padding: 20px; border-radius: 12px; margin-bottom: 15px; border-right: 4px solid var(--gold);}
.comment-header {display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 700; color: #fff;}
.comment-stars {color: var(--gold); font-size: 0.9rem;}
.disabled-star {color: #4a5568 !important;}
.comment-text {color: var(--text); line-height: 1.6;}
.comment-date {font-size: 0.8rem; color: #888;}

.form-container{background:var(--card);padding:50px 30px;border-radius:24px;max-width:700px;margin:auto;border:2px solid #2f3b4c;box-shadow:0 20px 50px rgba(0,0,0,0.3)}
input,select,textarea{width:100%;padding:14px;margin-bottom:20px;border-radius:12px;border:2px solid #2f3b4c;background:#11161d;color:#fff;font-size:16px;text-align:right;transition:0.3s}
input:focus,select:focus,textarea:focus{border-color:var(--gold);outline:none;box-shadow:0 0 10px rgba(255,215,0,0.2)}

.global-alert {background: #0f1115; color: #fff; padding: 16px 25px; text-align: center; font-weight: 700; position: fixed; top: 0; left:0; width: 100%; z-index: 10000; box-shadow: 0 4px 25px rgba(0,0,0,0.8); border-bottom: 3px solid var(--gold); display: flex; justify-content: center; align-items: center; gap: 15px; font-size: 15px; backdrop-filter: blur(10px);}
.global-alert i {color: var(--gold); font-size: 18px; text-shadow: 0 0 10px var(--gold); animation: float 2s ease infinite;}
.alert-close-btn {background: transparent; border: 2px solid rgba(255,215,0,0.3); color: var(--gold); padding: 2px 10px; border-radius: 6px; cursor: pointer; transition: 0.3s; font-weight: 900;}
.alert-close-btn:hover {background: var(--gold); color: #000; box-shadow: 0 0 10px var(--gold);}

.success-box {padding: 40px 20px !important; text-align: center !important; display: flex !important; flex-direction: column; align-items: center; justify-content: center; width: 100% !important;}
.success-glow-icon {width: 80px; height: 80px; background: rgba(255, 215, 0, 0.1); border: 3px solid var(--gold); color: var(--gold); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 35px; margin-bottom: 25px; animation: pulseGlow 2.5s infinite; text-shadow: 0 0 15px var(--gold);}
.success-title-text {color: var(--gold) !important; font-weight: 900 !important; font-size: 1.6rem !important; margin-bottom: 15px !important; display: block !important; text-shadow: 0 0 10px rgba(255,215,0,0.3);}
.success-desc-text {color: var(--text) !important; font-size: 1.1rem !important; font-weight: 600 !important; line-height: 1.8 !important; display: block !important; max-width: 500px;}

.modal-overlay {position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(8px); z-index: 2000; display: none; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s ease;}
.modal-overlay.active {display: flex; opacity: 1;}
.auth-modal {background: var(--card); border: 2px solid #2f3b4c; border-radius: 24px; width: 90%; max-width: 440px; padding: 35px 25px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); position: relative; animation: fadeIn 0.4s ease;}
.close-modal {position: absolute; top: 15px; left: 15px; background: transparent; border: none; color: var(--text); font-size: 22px; cursor: pointer; transition: 0.2s;}
.close-modal:hover {color: #ff4d4d;}
.modal-tabs {display: flex; border-bottom: 2px solid #2f3b4c; margin-bottom: 25px;}
.modal-tab {flex: 1; text-align: center; padding: 12px; cursor: pointer; font-weight: 700; color: var(--text); font-size: 16px; transition: 0.3s;}
.modal-tab.active {color: var(--gold); border-bottom: 3px solid var(--gold); margin-bottom: -2px;}

footer{text-align:center;padding:30px 15px;background:#050608;color:var(--text);font-size:15px;border-top:1px solid #11161d}

@media (max-width: 992px) {
    nav{flex-direction: column; gap: 12px; padding: 12px 5%; text-align:center; position: static;}
    nav .links{gap: 10px; flex-wrap: wrap; justify-content: center; width: 100%;}
    .hero{padding-top: 40px;}
    .hero h1{font-size: 2.8rem;}
}
</style></head><body>

{% if auth_error %}
<div class="global-alert" id="globalAlert">
    <span><i class="fa-solid fa-shield-halved"></i> {{ auth_error }}</span>
    <button class="alert-close-btn" onclick="document.getElementById('globalAlert').style.display='none'">إغلاق</button>
</div>
{% endif %}

<nav>
    <div class="logo"><i class="fa-solid fa-crown"></i> سيد اللعبة</div>
    <div class="links">
        <a href="#home">الرئيسية</a>
        <a href="#about">عن المستر</a>
        <a href="#features">المميزات</a>
        <a href="#prices">الأسعار</a>
        <a href="#gallery">صورنا</a>
        <a href="#faq">الأسئلة الشائعة</a>
        <a href="#testimonials">آراء الطلاب</a>
        <a href="#book">الحجز الحالي</a>
        
        {% if session.get('user_name') %}
            <div class="user-badge">
                <i class="fa-solid fa-user-tie" style="color:var(--gold)"></i> {{ session['user_name'] }}
                <a href="/logout" class="logout-link"><i class="fa-solid fa-right-from-bracket"></i> خروج</a>
            </div>
        {% else %}
            <button class="nav-auth-btn" onclick="openAuthModal('login')"><i class="fa-solid fa-right-to-bracket"></i> دخول / تسجيل</button>
        {% endif %}
    </div>
</nav>

<section class="hero" id="home">
    <div class="hero-content">
        <h1>سيد اللعبة <i class="fa-solid fa-bolt" style="color: var(--gold); font-size: 3rem; display: inline-block;"></i></h1>
        <p>مستر الرياضيات الأول الذي يدمج بين بساطة الشرح والحل الاحترافي لتضمن الدرجة النهائية بكل سهولة.</p>
        {% if already_booked %}
            <a href="#book" class="btn"><i class="fa-solid fa-clipboard-check"></i> عرض حالة حجزك الحالي</a>
        {% else %}
            <a href="#book" class="btn"><i class="fa-solid fa-calendar-days"></i> احجز مقعدك الآن | 40 جنيه</a>
        {% endif %}
    </div>
</section>

<div class="modal-overlay" id="authModalOverlay">
    <div class="auth-modal">
        <button class="close-modal" onclick="closeAuthModal()">×</button>
        <div class="modal-tabs">
            <div class="modal-tab" id="tab-login" onclick="switchTab('login')">تسجيل الدخول</div>
            <div class="modal-tab" id="tab-register" onclick="switchTab('register')">حساب جديد</div>
        </div>

        <form id="loginForm" action="/login" method="POST">
            <input type="email" name="email" placeholder="البريد الإلكتروني" required>
            <input type="password" name="password" placeholder="كلمة المرور" required>
            <button class="btn" style="width: 100%; border-radius: 12px; font-size:16px; padding:10px;"><i class="fa-solid fa-right-to-bracket"></i> دخول</button>
        </form>

        <form id="registerForm" action="/register" method="POST" style="display: none;">
            <input type="text" name="name" placeholder="الاسم الكامل للطالب" required>
            <input type="email" name="email" placeholder="البريد الإلكتروني" required>
            <input type="password" name="password" placeholder="إنشاء كلمة مرور" required>
            <button class="btn" style="width: 100%; border-radius: 12px; font-size:16px; padding:10px;"><i class="fa-solid fa-user-plus"></i> إنشاء الحساب</button>
        </form>
    </div>
</div>

<section id="about">
    <div class="stats-container">
        <div class="stat-card"><i class="fa-solid fa-user-graduate"></i><div class="stat-number">170</div><div class="stat-label">طالب متفوق</div></div>
        <div class="stat-card"><i class="fa-solid fa-award"></i><div class="stat-number">4</div><div class="stat-label">سنوات خبرة</div></div>
        <div class="stat-card"><i class="fa-solid fa-star"></i><div class="stat-number">60.4%</div><div class="stat-label">نسبة النجاح</div></div>
    </div>

    <h2 class="section-title">من هو مستر الرياضيات؟</h2>
    <div class="about">
        <img src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=2070">
        <div class="about-text">
            <h3 style="color:var(--gold);font-size:1.9rem;margin-bottom:15px;">خبرة متراكمة في تبسيط الرياضيات</h3>
            <p>الرياضيات ليست حفظ قوانين، الرياضيات لعبة وإذا فهمت أسرارها ستصبح هدافاً فيها. نحن نركز على الفهم العميق للوصول إلى التميز الحقيقي وليس الحفظ المؤقت.</p>
        </div>
    </div>
</section>

<section id="features">
    <h2 class="section-title">لماذا كبسولات سيد اللعبة؟</h2>
    <div class="grid-features">
        <div class="feat-box"><i class="fa-solid fa-brain"></i><h3>خرائط ذهنية متطورة</h3><p>ملخصات بصرية تختصر الفصول الطويلة والمعقدة في ورقة واحدة سهلة التذكر.</p></div>
        <div class="feat-box"><i class="fa-solid fa-laptop-code"></i><h3>متابعة على مدار الساعة</h3><p>فريق كامل متواجد للإجابة على جميع استفسارات الطلاب عبر الواتساب طوال الأسبوع.</p></div>
        <div class="feat-box"><i class="fa-solid fa-sheet-plastic"></i><h3>امتحانات دورية</h3><p>اختبارات ذكية تقيس مستوى الطالب الحقيقي وتكشف نقاط الضعف لمعالجتها فوراً.</p></div>
    </div>
</section>

<section id="prices">
    <h2 class="section-title">أسعار حجز المحاضرات</h2>
    <div class="pricing-grid">
        <div class="price-card">
            <h3>الكبسولة الشاملة</h3>
            <div class="price-amount">40 ج</div>
            <span class="price-period">للحصة الواحدة فقط</span>
            <ul class="price-features">
                <li><i class="fa-solid fa-check"></i> حضور المحاضرة التفاعلية كاملة</li>
                <li><i class="fa-solid fa-check"></i> الحصول على المذكرة الورقية مجاناً</li>
                <li><i class="fa-solid fa-check"></i> مراجعة الامتحانات والواجبات الدورية</li>
                <li><i class="fa-solid fa-check"></i> الدخول لجروب الدعم السري</li>
            </ul>
            <a href="#book" class="btn" style="width: 100%; text-align:center;">احجز مقعدك الآن</a>
        </div>
    </div>
</section>

<section id="gallery">
    <h2 class="section-title">بيئة الدراسة والسنتر</h2>
    <div class="gallery">
        <img src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=2070">
        <img src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=2070">
    </div>
</section>

<section id="faq">
    <h2 class="section-title">الأسئلة الشائعة</h2>
    <div class="faq-container">
        <div class="faq-item">
            <button class="faq-btn" onclick="toggleFaq(this)">كيف يمكنني دفع رسوم الكبسولة؟ <i class="fa-solid fa-chevron-down"></i></button>
            <div class="faq-content"><p>يتم الدفع يدوياً عند حضورك إلى السنتر مباشرة في موعد الحصة أو من خلال فودافون كاش بالتنسيق مع الدعم.</p></div>
        </div>
        <div class="faq-item">
            <button class="faq-btn" onclick="toggleFaq(this)">هل الكبسولات تغطي المنهج بأكمله؟ <i class="fa-solid fa-chevron-down"></i></button>
            <div class="faq-content"><p>نعم، الكبسولات مصممة بطريقة ذكية لتشمل كل الأفكار الهامة والأسئلة المتوقعة في الامتحان النهائي.</p></div>
        </div>
    </div>
</section>

<section id="testimonials">
    <h2 class="section-title">لوحة آراء وتعليقات الطلاب</h2>
    <div class="comments-section">
        <div class="comments-list">
            {% for comment in comments %}
                <div class="comment-item">
                    <div class="comment-header">
                        <span><i class="fa-solid fa-user-circle"></i> {{ comment.name }}</span>
                        <span class="comment-stars">
                            {% for i in range(comment.rating|int) %} <i class="fas fa-star"></i> {% endfor %}
                            {% for i in range(5 - comment.rating|int) %} <i class="fas fa-star disabled-star"></i> {% endfor %}
                        </span>
                    </div>
                    <p class="comment-text">{{ comment.text }}</p>
                    <div class="comment-date" style="text-align: left;"><i class="fa-solid fa-clock"></i> {{ comment.date }}</div>
                </div>
            {% endfor %}
        </div>

        <h3 style="color: var(--gold); margin-bottom: 15px;"><i class="fa-solid fa-pen-to-square"></i> اكتب تعليقك وتقييمك للمستر</h3>
        <form action="/add_comment" method="POST">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <input name="c_name" value="{{ session.get('user_name', '') }}" placeholder="اسمك الكريم" required {% if session.get('user_name') %} disabled style="background:#222; color:#aaa;" {% endif %}>
                <select name="c_rating" required>
                    <option value="5">ممتاز (5 نجوم)</option>
                    <option value="4">جيد جداً (4 نجوم)</option>
                    <option value="3">متوسط (3 نجوم)</option>
                </select>
            </div>
            <textarea name="c_text" rows="3" placeholder="اكتب رأيك بصراحة في الشرح والملخصات..." required></textarea>
            <button class="btn" style="width: 100%; border-radius: 10px;"><i class="fa-solid fa-paper-plane"></i> نشر التعليق فوراً</button>
        </form>
    </div>
</section>

<section id="book">
    <h2 class="section-title">احجز مكانك الآن</h2>
    <div class="form-container">
        {% if already_booked %}
            <div class="success-box">
                <div class="success-glow-icon"><i class="fa-solid fa-crown"></i></div>
                <div class="success-title-text">تم تسجيل الحجز بنجاح مسبقاً</div>
                <div class="success-desc-text">المقعد محجوز، وجاري مراجعة البيانات للتواصل عبر رقم الواتساب لتأكيد موعد الحصة الأولى.</div>
            </div>
        {% else %}
            <form action="/" method="POST">
                <input name="name" value="{{ session.get('user_name', '') }}" placeholder="الاسم بالكامل" required {% if session.get('user_name') %} disabled style="background:#222; color:#aaa;" {% endif %}>
                <input name="phone" type="tel" placeholder="رقم الواتساب (مثال: 01xxxxxxxxx)" required>
                <select name="grade" required>
                    <option value="">اختر الصف الدراسي</option>
                    <option>الصف الأول الثانوي</option>
                    <option>الصف الثاني الثانوي</option>
                    <option>الصف الثالث الثانوي</option>
                </select>
                <input type="date" name="date" required>
                <textarea name="note" rows="3" placeholder="أي ملاحظات أو استفسارات تود إعلام المستر بها.."></textarea>
                <button class="btn" style="width:100%; border-radius:12px;"><i class="fa-solid fa-paper-plane"></i> تأكيد وإرسال طلب الحجز - 40 ج</button>
            </form>
        {% endif %}
    </div>
</section>

<footer>© 2026 سيد اللعبة - مستر الرياضيات. جميع الحقوق محفوظة.</footer>

<script>
function openAuthModal(mode) {
    document.getElementById('authModalOverlay').classList.add('active');
    switchTab(mode);
}
function closeAuthModal() {
    document.getElementById('authModalOverlay').classList.remove('active');
}
function switchTab(mode) {
    if(mode === 'login') {
        document.getElementById('tab-login').classList.add('active');
        document.getElementById('tab-register').classList.remove('active');
        document.getElementById('loginForm').style.display = 'block';
        document.getElementById('registerForm').style.display = 'none';
    } else {
        document.getElementById('tab-register').classList.add('active');
        document.getElementById('tab-login').classList.remove('active');
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('registerForm').style.display = 'block';
    }
}
function toggleFaq(btn) {
    const content = btn.nextElementSibling;
    const icon = btn.querySelector('i');
    if (content.style.maxHeight && content.style.maxHeight !== "0px") {
        content.style.maxHeight = "0px";
        content.style.paddingTop = "0px";
        content.style.paddingBottom = "0px";
        icon.className = "fa-solid fa-chevron-down";
    } else {
        content.style.maxHeight = content.scrollHeight + 40 + "px";
        content.style.paddingTop = "15px";
        content.style.paddingBottom = "15px";
        icon.className = "fa-solid fa-chevron-up";
    }
}
</script>
</body></html>"""

def admin_bot():
    last_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_id+1}"
            res = requests.get(url, timeout=10).json()
            for update in res.get('result', []):
                last_id = update['update_id']
                if 'callback_query' in update:
                    callback = update['callback_query']
                    chat_id = callback['message']['chat']['id']
                    message_id = callback['message']['message_id']
                    data_action = callback['data']
                    
                    if str(chat_id) == ADMIN_CHAT_ID and data_action.startswith("del_"):
                        comment_id = data_action.replace("del_", "")
                        comments = load_comments()
                        updated_comments = [c for c in comments if str(c.get('id')) != comment_id]
                        save_comments(updated_comments)
                        
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery", data={"callback_query_id": callback['id'], "text": "❌ تم حذف التعليق!"})
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText", data={
                            "chat_id": ADMIN_CHAT_ID, "message_id": message_id,
                            "text": f"{callback['message']['text']}\n\n🛑 <b>[تم حذف التعليق]</b>", "parse_mode": "HTML"
                        })
                    continue
        except: pass
        time.sleep(1)

@app.route('/', methods=['GET','POST'])
def home():
    already_booked = request.cookies.get('has_booked') == 'true'
    comments = load_comments()
    auth_error = session.pop('auth_error', None)

    if request.method == 'POST':
        if already_booked:
            return make_response(render_template_string(HTML, already_booked=True, comments=comments, auth_error=auth_error))
            
        name = session.get('user_name') if session.get('user_name') else request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        grade = request.form.get('grade', '').strip()
        date = request.form.get('date', '').strip()
        note = request.form.get('note', '').strip()

        data = load_bookings()
        booking = {'name': name, 'phone': phone, 'grade': grade, 'date': date, 'note': note if note else "لا يوجد", 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        data.append(booking)
        save_bookings(data)
        
        admin_msg = f"<b>حجز جديد!</b>\n\n<b>الاسم:</b> {name}\n<b>الرقم:</b> {phone}\n<b>الصف:</b> {grade}"
        threading.Thread(target=send_telegram, args=(admin_msg,)).start()
        
        resp = make_response(render_template_string(HTML, already_booked=True, comments=comments, auth_error=auth_error))
        resp.set_cookie('has_booked', 'true', max_age=31536000) 
        return resp

    return render_template_string(HTML, already_booked=already_booked, comments=comments, auth_error=auth_error)

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    
    users = load_users()
    if email in users:
        session['auth_error'] = "هذا البريد الإلكتروني مسجل بموقعنا بالفعل، تفضل بتسجيل الدخول."
        return redirect(url_for('home'))
        
    users[email] = {
        "name": name,
        "password": generate_password_hash(password)
    }
    save_users(users)
    
    session['user_email'] = email
    session['user_name'] = name
    return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    
    users = load_users()
    if email in users and check_password_hash(users[email]['password'], password):
        session['user_email'] = email
        session['user_name'] = users[email]['name']
    else:
        session['auth_error'] = "تأكد من كتابة البريد الإلكتروني أو كلمة المرور بشكل صحيح وأعد المحاولة."
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/add_comment', methods=['POST'])
def add_comment():
    c_name = session.get('user_name') if session.get('user_name') else request.form.get('c_name', '').strip()
    c_text = request.form.get('c_text', '').strip()
    c_rating = request.form.get('c_rating', '5')

    if c_name and c_text and not check_profanity(c_text):
        comments = load_comments()
        comment_id = str(int(time.time() * 1000))
        new_comment = {"id": comment_id, "name": c_name, "rating": c_rating, "text": c_text, "date": datetime.date.today().strftime("%Y-%m-%d")}
        comments.insert(0, new_comment)
        save_comments(comments)
        
        tg_msg = f"📝 <b>تعليق جديد!</b>\n<b>الاسم:</b> {c_name}\n<b>التعليق:</b> {c_text}"
        reply_markup = {"inline_keyboard": [[{"text": "❌ حذف التعليق", "callback_data": f"del_{comment_id}"}]]}
        threading.Thread(target=send_telegram, args=(tg_msg, reply_markup)).start()

    return redirect(url_for('home'))

if __name__ == '__main__':
    if TELEGRAM_TOKEN != "" and TELEGRAM_TOKEN != "حط_التوكن_هنا":
        threading.Thread(target=admin_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
