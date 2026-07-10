from flask import Flask, render_template_string, request, make_response, redirect, url_for
import json, os, datetime, threading, time
import requests

app = Flask(__name__)
BOOKINGS_FILE = 'bookings.json'
COMMENTS_FILE = 'comments.json'
PRICE = 40  

TELEGRAM_TOKEN = "8801743115:AAGN2S0DwR5lSMwYMjmsxLyD4E8LJ62mdZI"
ADMIN_CHAT_ID = "7728398907"

# قائمة الكلمات المحظورة لمنع العبارات غير اللائقة
BAD_WORDS = [
    "شتم", "كلب", "حمار", "غبي", "يا ابن", "عرص", "خول", "شرموط", "تفه", "كس", "زب", "منيك", "قذر", "وسخ"
]

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
        {"name": "سارة أحمد", "rating": "5", "text": "مستر ممتاز جداً والرياضيات بقت أسهل مادة عندي بفضله", "date": "2026-07-10"},
        {"name": "محمد كريم", "rating": "4", "text": "أفضل كبسولات ليلة امتحان ممكن تاخدها في حياتك", "date": "2026-07-11"}
    ]

def save_comments(data):
    json.dump(data, open(COMMENTS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def check_profanity(text):
    for word in BAD_WORDS:
        if word in text.lower():
            return True
    return False

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try: requests.post(url, data=data, timeout=10)
    except: pass

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

nav{position:fixed;top:0;width:100%;background:rgba(11, 12, 16, 0.9);backdrop-filter:blur(12px);padding:15px 5%;display:flex;justify-content:space-between;align-items:center;z-index:100;box-shadow:0 4px 20px rgba(0,0,0,0.6);border-bottom:1px solid rgba(255,215,0,0.1)}
nav .logo{font-weight:900;color:var(--gold);font-size:22px;display:flex;align-items:center;gap:10px;text-shadow:0 0 10px rgba(255,215,0,0.3)}
nav .links{display:flex;gap:20px}
nav a{color:#fff;text-decoration:none;font-weight:700;transition:0.3s;font-size:15px}
nav a:hover{color:var(--gold)}

.hero{min-height:100vh;background:linear-gradient(rgba(11,12,16,0.75),rgba(11,12,16,0.95)),url('https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=2070') center/cover fixed; display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 20px 60px 20px}
.hero-content{animation:fadeIn 1s ease; max-width:800px}
.hero h1{font-size:4rem;font-weight:900;color:var(--gold);margin-bottom:20px;text-shadow:0 0 25px rgba(255,215,0,0.5)}
.hero p{font-size:1.3rem;color:var(--text);margin-bottom:35px;line-height:1.8}
.btn{background:linear-gradient(45deg, var(--gold), #ffb700);color:#000;padding:14px 40px;border:none;border-radius:50px;font-size:18px;font-weight:900;cursor:pointer;transition:0.4s;text-decoration:none;display:inline-block;box-shadow:0 5px 15px rgba(255,215,0,0.3)}
.btn:hover{transform:scale(1.05);box-shadow:0 0 35px var(--gold)}

section{padding:80px 5%;max-width:1300px;margin:auto}
.section-title{text-align:center;font-size:2.5rem;margin-bottom:50px;color:var(--gold);position:relative}
.section-title::after{content:'';position:absolute;bottom:-10px;left:50%;transform:translateX(-50%);width:60px;height:3px;background:var(--gold);border-radius:2px}

.about{display:flex;gap:50px;align-items:center;flex-wrap:wrap;justify-content:center}
.about img{width:100%;max-width:450px;height:300px;object-fit:cover;border-radius:20px;animation:float 4s ease-in-out infinite, glow 3s ease-in-out infinite;border:3px solid var(--gold)}
.about-text{flex:1;min-width:300px;font-size:1.15rem;line-height:2;color:var(--text)}
.features-list {list-style: none; margin-top: 20px;}
.features-list li {margin-bottom: 12px; display: flex; align-items: center; gap: 12px; font-weight: 600}
.features-list i {color: var(--gold); font-size: 1.3rem;}

.stats-container{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;text-align:center;margin-top:40px}
.stat-box{background:rgba(31,40,51,0.6);padding:20px;border-radius:15px;border:1px solid #2f3b4c}
.stat-box i{font-size:2rem;color:var(--gold);margin-bottom:10px}
.stat-number{font-size:2rem;font-weight:900;color:#fff}
.stat-title{color:var(--text);font-size:1rem}

.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}
.gallery img{width:100%;height:240px;object-fit:cover;border-radius:15px;transition:0.4s;border:2px solid #333}
.gallery img:hover{transform:scale(1.05) translateY(-5px);border-color:var(--gold);box-shadow:0 10px 25px rgba(255,215,0,0.3)}

.pricing{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:25px}
.card{background:var(--card);padding:35px 25px;border-radius:20px;text-align:center;border:2px solid #2f3b4c;transition:0.4s}
.card:hover{transform:translateY(-10px);border-color:var(--gold);box-shadow:0 15px 40px rgba(255,215,0,0.15)}
.card h3{color:var(--gold);font-size:1.8rem;margin-bottom:15px}
.price{font-size:3.2rem;font-weight:900;color:#fff;margin-bottom:15px}
.price span{font-size:1.1rem;color:var(--text)}

.comments-section {background: rgba(31, 40, 51, 0.3); padding: 40px 20px; border-radius: 20px; border: 1px solid #2f3b4c; margin-top: 30px;}
.comments-list {max-height: 400px; overflow-y: auto; margin-bottom: 30px; padding-right: 10px;}
.comment-item {background: var(--card); padding: 20px; border-radius: 12px; margin-bottom: 15px; border-right: 4px solid var(--gold);}
.comment-header {display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 700; color: #fff;}
.comment-stars {color: var(--gold); font-size: 0.9rem;}
.disabled-star {color: #4a5568 !important;}
.comment-text {color: var(--text); line-height: 1.6;}
.comment-date {font-size: 0.8rem; color: #888;}

.faq-container{max-width:800px;margin:auto}
.faq-item{background:var(--card);margin-bottom:15px;border-radius:10px;border:1px solid #2f3b4c;overflow:hidden}
.faq-question{padding:20px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:1.1rem;transition:0.3s}
.faq-question:hover{background:rgba(255,215,0,0.05)}
.faq-answer{padding:0 20px;max-height:0;overflow:hidden;transition:max-height 0.3s ease;color:var(--text);line-height:1.8}

.form-container{background:var(--card);padding:50px 30px;border-radius:24px;max-width:700px;margin:auto;border:2px solid #2f3b4c;box-shadow:0 20px 50px rgba(0,0,0,0.3)}
input,select,textarea{width:100%;padding:14px;margin-bottom:20px;border-radius:12px;border:2px solid #2f3b4c;background:#11161d;color:#fff;font-size:16px;text-align:right;transition:0.3s}
input:focus,select:focus,textarea:focus{border-color:var(--gold);outline:none;box-shadow:0 0 10px rgba(255,215,0,0.2)}

.error-msg {background: #ff4d4d; color: #fff; padding: 12px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; text-align: center;}

/* تنسيق فك تشابك وكسر النصوص لـ صندوق حجز المتكرر */
.success-box {
    padding: 10px 5px !important;
    text-align: center !important;
    display: block !important;
    width: 100% !important;
}
.success-title-text {
    color: #00ff88 !important;
    font-weight: 700 !important;
    font-size: 1.4rem !important;
    margin-top: 10px !important;
    margin-bottom: 15px !important;
    display: block !important;
    white-space: normal !important;
}
.success-desc-text {
    color: #ffffff !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    line-height: 1.7 !important;
    display: block !important;
    white-space: normal !important;
}
.success-icon {font-size: 4.5rem; color: #00ff88; margin-bottom: 15px; display: inline-block; animation:float 3s ease-in-out infinite}

footer{text-align:center;padding:30px 15px;background:#050608;color:var(--text);font-size:15px;border-top:1px solid #11161d}

@media (max-width: 768px) {
    nav{flex-direction: column; gap: 15px; padding: 15px 5%; text-align:center}
    nav .links{gap: 12px; flex-wrap: wrap; justify-content: center;}
    nav a{font-size: 13px;}
    .hero h1{font-size: 2.8rem;}
    .hero p{font-size: 1.1rem;}
    .section-title{font-size: 2rem;}
    .btn{width: 100%; text-align: center;}
}
</style></head><body>

<nav>
    <div class="logo">
        <i class="fa-solid fa-crown"></i> سيد اللعبة
    </div>
    <div class="links">
        <a href="#home">الرئيسية</a>
        <a href="#about">عن المستر</a>
        <a href="#gallery">صورنا</a>
        <a href="#pricing">الأسعار</a>
        <a href="#testimonials">آراء الطلاب</a>
        <a href="#faq">الأسئلة الشائعة</a>
        <a href="#book">الحجز الحالي</a>
    </div>
</nav>

<section class="hero" id="home">
    <div class="hero-content">
        <h1>سيد اللعبة <i class="fa-solid fa-bolt" style="color: var(--gold); font-size: 3rem; display: inline-block;"></i></h1>
        <p>مستر الرياضيات الأول الذي يدمج بين بساطة الشرح والحل الاحترافي لتضمن الدرجة النهائية بكل سهولة وأنت مستمتع بالرحلة.</p>
        {% if already_booked %}
            <a href="#book" class="btn"><i class="fa-solid fa-clipboard-check"></i> عرض حالة حجزك الحالي</a>
        {% else %}
            <a href="#book" class="btn"><i class="fa-solid fa-calendar-days"></i> احجز مقعدك الآن | 40 جنيه</a>
        {% endif %}
    </div>
</section>

<section id="about">
    <h2 class="section-title">من هو مستر الرياضيات؟</h2>
    <div class="about">
        <img src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?q=80&w=2070">
        <div class="about-text">
            <h3 style="color:var(--gold);font-size:1.9rem;margin-bottom:15px;">خبرة أكثر من 10 سنوات في تبسيط الرياضيات</h3>
            <p>الرياضيات ليست حفظ قوانين، الرياضيات لعبة وإذا فهمت أسرارها ستصبح هدافاً فيها. نقدم لك نظاماً تعليمياً متكاملاً يشمل:</p>
            <ul class="features-list">
                <li><i class="fa-solid fa-square-root-variable"></i> مجموعات نخبة صغيرة (أقصى حد 8 طلاب للتركيز الشديد)</li>
                <li><i class="fa-solid fa-medal"></i> تقييمات وامتحانات دورية بعد كل حصة مباشرة</li>
                <li><i class="fa-solid fa-file-invoice"></i> مذكرات حصرية وتلخيصات كبسولة ليلة الامتحان</li>
                <li><i class="fa-solid fa-headset"></i> دعم ومتابعة واستفسارات 24 ساعة عبر الواتساب</li>
            </ul>
            
            <div class="stats-container">
                <div class="stat-box">
                    <i class="fa-solid fa-user-graduate"></i>
                    <div class="stat-number">+1500</div>
                    <div class="stat-title">طالب متميز</div>
                </div>
                <div class="stat-box">
                    <i class="fa-solid fa-star-and-crescent"></i>
                    <div class="stat-number">10</div>
                    <div class="stat-title">سنوات خبرة</div>
                </div>
                <div class="stat-box">
                    <i class="fa-solid fa-certificate"></i>
                    <div class="stat-number">%100</div>
                    <div class="stat-title">نسبة نجاح</div>
                </div>
            </div>
        </div>
    </div>
</section>

<section id="gallery">
    <h2 class="section-title">بيئة الدراسة والسنتر</h2>
    <div class="gallery">
        <img src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=2070">
        <img src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=2070">
        <img src="https://images.unsplash.com/photo-1544535830-9df3f56fff6a?q=80&w=2070">
        <img src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=2071">
    </div>
</section>

<section id="pricing">
    <h2 class="section-title">الباقات والاشتراكات</h2>
    <div class="pricing">
        <div class="card">
            <h3>الحصة الفردية</h3>
            <div class="price">40 <span>جنيه</span></div>
            <p>حصة مدتها ساعتين شاملة الشرح والتطبيق العملي وحل الواجب الفوري.</p>
        </div>
        <div class="card" style="border-color:var(--gold); background: rgba(255,215,0,0.02)">
            <h3>باقة الـ 4 حصص</h3>
            <div class="price">150 <span>جنيه</span></div>
            <p>توفير خاص ومتابعة دورية وتقارير أداء ترسل لولي الأمر أسبوعياً.</p>
        </div>
        <div class="card">
            <h3>الباقة الشهرية الكاملة</h3>
            <div class="price">280 <span>جنيه</span></div>
            <p>8 حصص كاملة ومراجعات مجانية وامتحانات شاملة بجوائز للمتفوقين.</p>
        </div>
    </div>
</section>

<section id="testimonials">
    <h2 class="section-title">لوحة آراء وتعليقات الطلاب</h2>
    <div class="comments-section">
        
        {% if comment_error %}
            <div class="error-msg"><i class="fa-solid fa-triangle-exclamation"></i> {{ comment_error }}</div>
        {% endif %}

        <div class="comments-list">
            {% for comment in comments %}
                <div class="comment-item">
                    <div class="comment-header">
                        <span><i class="fa-solid fa-user-circle"></i> {{ comment.name }}</span>
                        <span class="comment-stars">
                            {% for i in range(comment.rating|int) %}
                                <i class="fas fa-star"></i>
                            {% endfor %}
                            {% for i in range(5 - comment.rating|int) %}
                                <i class="fas fa-star disabled-star"></i>
                            {% endfor %}
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
                <input name="c_name" placeholder="اسمك الكريم" required>
                <select name="c_rating" required>
                    <option value="5">ممتاز (5 نجوم)</option>
                    <option value="4">جيد جداً (4 نجوم)</option>
                    <option value="3">متوسط (3 نجوم)</option>
                    <option value="2">مقبول (نجمتين)</option>
                    <option value="1">ضعيف (نجمة واحدة)</option>
                </select>
            </div>
            <textarea name="c_text" rows="3" placeholder="اكتب رأيك بصراحة في الشرح والملخصات..." required></textarea>
            <button class="btn" style="width: 100%; border-radius: 10px;"><i class="fa-solid fa-paper-plane"></i> نشر التعليق فوراً</button>
        </form>
    </div>
</section>

<section id="faq">
    <h2 class="section-title">الأسئلة الشائعة</h2>
    <div class="faq-container">
        <div class="faq-item">
            <div class="faq-question">أين مكان السنتر والمجموعات؟ <i class="fas fa-chevron-down"></i></div>
            <div class="faq-answer"><p>بعد تأكيد الحجز مباشرة، سيقوم الفريق الإداري بالتواصل معك عبر الواتساب لتحديد فرع السنتر الأقرب لك وإرسال الموقع الجغرافي والمواعيد بالتفصيل.</p></div>
        </div>
        <div class="faq-item">
            <div class="faq-question">هل يوجد شرح مخصص للأجزاء الصعبة المتراكمة؟ <i class="fas fa-chevron-down"></i></div>
            <div class="faq-answer"><p>نعم، يتم تقديم حصص تأسيسية ومراجعة سريعة لأي قواعد رياضية سابقة يحتاجها الطالب حتى يستوعب المنهج الحالي بيسر.</p></div>
        </div>
    </div>
</section>

<section id="book">
    <h2 class="section-title">احجز مكانك الآن</h2>
    <div class="form-container">
        {% if already_booked %}
            <div class="success-box">
                <i class="fa-solid fa-circle-check success-icon"></i>
                <div class="success-title-text">تم تسجيل الحجز بنجاح مسبقاً</div>
                <div class="success-desc-text">المقعد محجوز، وجاري مراجعة البيانات للتواصل عبر رقم الواتساب لتأكيد موعد الحصة الأولى.</div>
            </div>
        {% else %}
            <form action="/" method="POST">
                <input name="name" placeholder="الاسم بالكامل" required>
                <input name="phone" type="tel" placeholder="رقم الواتساب (مثال: 01xxxxxxxxx)" required>
                <select name="grade" required>
                    <option value="">اختر الصف الدراسي</option>
                    <option>الصف الأول الثانوي</option>
                    <option>الصف الثاني الثانوي</option>
                    <option>الصف الثالث الثانوي</option>
                </select>
                <input type="date" name="date" required>
                <textarea name="note" rows="3" placeholder="أي ملاحظات أو استفسارات تود إعلام المستر بها (مثلاً: أفضل مواعيد الصباح).."></textarea>
                <button class="btn" style="width:100%; border-radius:12px;"><i class="fa-solid fa-paper-plane"></i> تأكيد وإرسال طلب الحجز - 40 ج</button>
            </form>
        {% endif %}
    </div>
</section>

<footer>© 2026 سيد اللعبة - مستر الرياضيات. جميع الحقوق محفوظة.</footer>

<script>
document.querySelectorAll('.faq-question').forEach(item => {
    item.addEventListener('click', () => {
        const answer = item.nextElementSibling;
        const icon = item.querySelector('i');
        if (answer.style.maxHeight) {
            answer.style.maxHeight = null;
            answer.style.padding = "0 20px";
            icon.style.transform = "rotate(0deg)";
        } else {
            answer.style.maxHeight = answer.scrollHeight + 20 + "px";
            answer.style.padding = "10px 20px 20px 20px";
            icon.style.transform = "rotate(180deg)";
        }
    });
});
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
                message = update.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                text = message.get('text', '')
                
                if str(chat_id) == ADMIN_CHAT_ID:
                    if text == '/bookings':
                        data = load_bookings()
                        if not data: 
                            send_telegram("لا يوجد أي حجوزات مسجلة حتى الآن")
                            continue
                        msg = f"<b>قائمة الحجوزات الحالية ({len(data)} حجز):</b>\n\n"
                        for b in data[::-1][:10]:
                            msg += f"<b>الاسم:</b> {b['name']}\n<b>الرقم:</b> {b['phone']}\n<b>الصف:</b> {b['grade']}\n<b>التاريخ المطلوب:</b> {b['date']}\n<b>ملاحظة:</b> {b.get('note',' لا يوجد ')}\n<b>وقت الحجز:</b> {b['time']}\n---------------------------\n"
                        send_telegram(msg)
                    elif text == '/start':
                        send_telegram("أهلاً بك يا سيد اللعبة\n\nإليك الأوامر المتاحة لوحة التحكم:\n/bookings - لعرض آخر 10 حجوزات واردة للموقع فوراً.")
        except: pass
        time.sleep(2)

@app.route('/', methods=['GET','POST'])
def home():
    already_booked = request.cookies.get('has_booked') == 'true'
    comments = load_comments()

    if request.method == 'POST':
        if already_booked:
            return make_response(render_template_string(HTML, already_booked=True, comments=comments))
            
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        grade = request.form.get('grade', '').strip()
        date = request.form.get('date', '').strip()
        note = request.form.get('note', '').strip()

        if not name or not phone or not grade or not date:
            return "برجاء ملء كافة الحقول الأساسية قبل الإرسال!", 400

        data = load_bookings()
        booking = {
            'name': name,
            'phone': phone,
            'grade': grade,
            'date': date,
            'note': note if note else "لا يوجد",
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data.append(booking)
        save_bookings(data)
        
        admin_msg = f"<b>حجز جديد للموقع!</b>\n\n<b>الاسم:</b> {booking['name']}\n<b>رقم الواتساب:</b> {booking['phone']}\n<b>الصف:</b> {booking['grade']}\n<b>التاريخ المفضّل:</b> {booking['date']}\n<b>ملاحظات الطالب:</b> {booking['note']}"
        threading.Thread(target=send_telegram, args=(admin_msg,)).start()
        
        resp = make_response(render_template_string(HTML, already_booked=True, comments=comments))
        resp.set_cookie('has_booked', 'true', max_age=31536000) 
        return resp

    return render_template_string(HTML, already_booked=already_booked, comments=comments)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    c_name = request.form.get('c_name', '').strip()
    c_text = request.form.get('c_text', '').strip()
    c_rating = request.form.get('c_rating', '5')

    if check_profanity(c_name) or check_profanity(c_text):
        comments = load_comments()
        already_booked = request.cookies.get('has_booked') == 'true'
        return render_template_string(HTML, already_booked=already_booked, comments=comments, comment_error="عذراً، يحتوي تعليقك أو اسمك على كلمات غير لائقة ومحظورة في الموقع!")

    if c_name and c_text:
        comments = load_comments()
        new_comment = {
            "name": c_name,
            "rating": c_rating,
            "text": c_text,
            "date": datetime.date.today().strftime("%Y-%m-%d")
        }
        comments.insert(0, new_comment)
        save_comments(comments)
        
        threading.Thread(target=send_telegram, args=(f"📝 <b>تعليق جديد بالموقع!</b>\n<b>الاسم:</b> {c_name}\n<b>التقييم:</b> {c_rating} نجوم\n<b>التعليق:</b> {c_text}",)).start()

    return redirect(url_for('home'))

if __name__ == '__main__':
    if TELEGRAM_TOKEN != "حط_التوكن_هنا" and TELEGRAM_TOKEN != "":
        threading.Thread(target=admin_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
