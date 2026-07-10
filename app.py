from flask import Flask, render_template_string, request, make_response
import json, os, datetime, threading, time
import requests

app = Flask(__name__)
BOOKINGS_FILE = 'bookings.json'
SETTINGS_FILE = 'settings.json'

TELEGRAM_TOKEN = "8801743115:AAGN2S0DwR5lSMwYMjmsxLyD4E8LJ62mdZI"
ADMIN_CHAT_ID = "7728398907"

DEFAULT_SETTINGS = {
    "price_single": "40",
    "price_4_classes": "150",
    "price_month": "280",
    "hero_title": "سيد اللعبة",
    "hero_desc": "مستر الرياضيات اللي هيخليك تقفل المادة وتجيب الدرجة النهائية",
    "about_title": "خبرة 10 سنين في اللعبة",
    "about_desc": 'مع المستر "سيد اللعبة" الرياضيات هتبقى لعبة في ايدك. شرح مبسط + حل امتحانات + متابعة مستمرة 24 ساعة على الواتساب.',
    "img_hero": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=2070",
    "img_about": "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=2032",
    "img_gallery1": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?q=80&w=1932",
    "img_gallery2": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=2022",
    "img_gallery3": "https://images.unsplash.com/photo-1599058917212-d750089bc07e?q=80&w=2070",
    "img_gallery4": "https://images.unsplash.com/photo-1562774053-701939374585?q=80&w=2071"
}

admin_state = {}

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        try: return json.load(open(BOOKINGS_FILE, encoding='utf-8'))
        except: return []
    return []

def save_bookings(data):
    json.dump(data, open(BOOKINGS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try: return json.load(open(SETTINGS_FILE, encoding='utf-8'))
        except: return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(data):
    json.dump(data, open(SETTINGS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def send_telegram(msg, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try: requests.post(url, data=data, timeout=10)
    except: pass

HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>{{ settings.hero_title }} - مستر الرياضيات</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
:root{--gold:#FFD700;--dark:#0a0a0a;--card:#111;--red:#ff0000}
*{margin:0;padding:0;font-family:'Cairo',tahoma;box-sizing:border-box;scroll-behavior:smooth}
body{background:var(--dark);color:#fff;overflow-x:hidden}

@keyframes float {0%,100%{transform:translateY(0)}50%{transform:translateY(-15px)}}
@keyframes glow {0%,100%{box-shadow:0 0 20px var(--gold)}50%{box-shadow:0 0 40px var(--gold)}}
@keyframes fadeIn{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}

nav{position:fixed;top:0;width:100%;background:rgba(0, 0, 0, 0.85);backdrop-filter:blur(10px);padding:15px 20px;display:flex;justify-content:space-between;align-items:center;z-index:100;box-shadow:0 2px 10px rgba(0,0,0,0.5)}
nav a{color:#fff;text-decoration:none;margin:0 8px;font-weight:700;transition:0.3s;font-size:14px}
nav a:hover{color:var(--gold)}

.hero{min-height:100vh;background:linear-gradient(rgba(0,0,0,0.6),rgba(0,0,0,0.8)),url('{{ settings.img_hero }}') center/cover; display:flex;align-items:center;justify-content:center;text-align:center;padding:80px 20px 40px 20px}
.hero-content{animation:fadeIn 1.2s ease; width:100%}
.hero h1{font-size:3rem;font-weight:900;color:var(--gold);margin-bottom:15px;text-shadow:0 0 20px var(--gold)}
.hero p{font-size:1.1rem;color:#ccc;margin-bottom:30px;line-height:1.6}
.btn{background:var(--gold);color:#000;padding:12px 35px;border:none;border-radius:50px;font-size:16px;font-weight:900;cursor:pointer;transition:0.3s;text-decoration:none;display:inline-block}
.btn:hover{transform:scale(1.05);box-shadow:0 0 30px var(--gold)}

section{padding:60px 20px;max-width:1300px;margin:auto}
.section-title{text-align:center;font-size:2.2rem;margin-bottom:40px;color:var(--gold)}

.about{display:flex;gap:30px;align-items:center;flex-wrap:wrap;justify-content:center}
.about img{width:100%;max-width:400px;height:auto;border-radius:20px;animation:float 3s ease-in-out infinite,glow 2s ease-in-out infinite}
.about-text{flex:1;min-width:280px;font-size:1.1rem;line-height:2}

.features-list {list-style: none; margin-top: 15px;}
.features-list li {margin-bottom: 10px; display: flex; align-items: center; gap: 10px;}
.features-list i {color: var(--gold); font-size: 1.2rem;}

.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px}
.gallery img{width:100%;height:220px;object-fit:cover;border-radius:15px;transition:0.4s}
.gallery img:hover{transform:scale(1.05);box-shadow:0 0 20px var(--gold)}

.pricing{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}
.card{background:var(--card);padding:25px;border-radius:20px;text-align:center;border:2px solid #333;transition:0.4s}
.card:hover{transform:translateY(-10px);border-color:var(--gold);box-shadow:0 15px 40px rgba(255,215,0,0.2)}
.card h3{color:var(--gold);font-size:1.6rem;margin-bottom:10px}
.price{font-size:2.8rem;font-weight:900;color:var(--gold)}
.price span{font-size:1rem;color:#aaa}

.form-container{background:var(--card);padding:40px 20px;border-radius:20px;max-width:650px;margin:auto;border:2px solid #333;text-align:center;}
input,select,textarea{width:100%;padding:12px;margin-bottom:15px;border-radius:10px;border:2px solid #333;background:#1a1a1a;color:#fff;font-size:16px;text-align:right;}
input:focus,textarea:focus{border-color:var(--gold);outline:none}

.success-box{padding:20px;color:#00ff88;font-weight:bold;font-size:1.3rem;line-height:1.8}
.success-icon {font-size: 4rem; color: #00ff88; margin-bottom: 15px; display: block;}

footer{text-align:center;padding:25px 15px;background:#000;color:#aaa;font-size:14px}

@media (max-width: 480px) {
    nav{flex-direction: column; gap: 10px; padding: 10px;}
    nav a{margin: 0 5px; font-size: 12px;}
    .hero h1{font-size: 2.3rem;}
    .hero p{font-size: 1rem;}
    .section-title{font-size: 1.8rem;}
    .btn{width: 100%; text-align: center; box-sizing: border-box;}
}
</style></head><body>

<nav>
    <div style="font-weight:900;color:var(--gold);font-size:20px; display:flex; align-items:center; gap:5px;">
        <i class="fa-solid fa-crown"></i> {{ settings.hero_title }}
    </div>
    <div>
        <a href="#home">الرئيسية</a>
        <a href="#about">عن المستر</a>
        <a href="#gallery">صورنا</a>
        <a href="#pricing">الاسعار</a>
        <a href="#book">الحجز</a>
    </div>
</nav>

<section class="hero" id="home">
    <div class="hero-content">
        <h1>{{ settings.hero_title }}</h1>
        <p>{{ settings.hero_desc }}</p>
        {% if already_booked %}
            <a href="#book" class="btn"><i class="fa-solid fa-clipboard-check"></i> عرض حالة الحجز الخاص بك</a>
        {% else %}
            <a href="#book" class="btn"><i class="fa-solid fa-calendar-days"></i> احجز محاضرتك بـ {{ settings.price_single }} جنيه</a>
        {% endif %}
    </div>
</section>

<section id="about">
    <h2 class="section-title">عن المستر</h2>
    <div class="about">
        <img src="{{ settings.img_about }}">
        <div class="about-text">
            <h3 style="color:var(--gold);font-size:1.8rem;margin-bottom:15px;text-align:center">{{ settings.about_title }}</h3>
            <p>{{ settings.about_desc }}</p>
            <ul class="features-list">
                <li><i class="fa-solid fa-circle-check"></i> مجموعات صغيرة 8 طلاب فقط</li>
                <li><i class="fa-solid fa-circle-check"></i> امتحان كل حصة</li>
                <li><i class="fa-solid fa-circle-check"></i> مراجعات مكثفة قبل الامتحان</li>
                <li><i class="fa-solid fa-circle-check"></i> متابعة اولياء الامور</li>
            </ul>
        </div>
    </div>
</section>

<section id="gallery">
    <h2 class="section-title">صور من السنتر والمحاضرات</h2>
    <div class="gallery">
        <img src="{{ settings.img_gallery1 }}">
        <img src="{{ settings.img_gallery2 }}">
        <img src="{{ settings.img_gallery3 }}">
        <img src="{{ settings.img_gallery4 }}">
    </div>
</section>

<section id="pricing">
    <h2 class="section-title">باقات واسعار</h2>
    <div class="pricing">
        <div class="card">
            <h3>الحصة الفردية</h3>
            <div class="price">{{ settings.price_single }}<span> جنيه</span></div>
            <p>حصة 2 ساعة - شرح + حل + واجب</p>
        </div>
        <div class="card" style="border-color:var(--gold)">
            <h3>باقة 4 حصص</h3>
            <div class="price">{{ settings.price_4_classes }}<span> جنيه</span></div>
            <p>وفر في الاشتراك - متابعة واتساب + ملازم</p>
        </div>
        <div class="card">
            <h3>باقة الشهر</h3>
            <div class="price">{{ settings.price_month }}<span> جنيه</span></div>
            <p>8 حصص + مراجعات + 2 امتحان شامل</p>
        </div>
    </div>
</section>

<section id="book">
    <h2 class="section-title">الحجز</h2>
    <div class="form-container">
        {% if already_booked %}
            <div class="success-box">
                <i class="fa-solid fa-circle-check success-icon"></i>
                تم الحجز بنجاح سابقاً!<br>
                لقد قمت بحجز محاضرتك بالفعل، وسنتواصل معك عبر الواتساب لتأكيد الموعد.
            </div>
        {% else %}
            <form method="POST">
                <input name="name" placeholder="الاسم الكامل" required>
                <input name="phone" placeholder="رقم الواتساب" required>
                <select name="grade" required>
                    <option value="">اختر الصف</option>
                    <option>اولى ثانوي</option>
                    <option>تانية ثانوي</option>
                    <option>تالتة ثانوي</option>
                </select>
                <input type="date" name="date" required>
                <textarea name="note" placeholder="ملاحظات - مثلا عايز مجموعة الصبح"></textarea>
                <button class="btn" style="width:100%"><i class="fa-solid fa-check-double"></i> تأكيد الحجز - {{ settings.price_single }} جنيه</button>
            </form>
        {% endif %}
    </div>
</section>

<footer>© 2026 {{ settings.hero_title }} - مستر الرياضيات. كل الحقوق محفوظة</footer>

</body></html>"""

def get_admin_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "عرض الحجوزات", "callback_data": "cmd_bookings"}],
            [{"text": "تعديل الصور", "callback_data": "menu_images"}, {"text": "تعديل النصوص", "callback_data": "menu_texts"}],
            [{"text": "تعديل الأسعار", "callback_data": "menu_prices"}]
        ]
    }

def admin_bot():
    last_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_id+1}"
            res = requests.get(url, timeout=10).json()
            for update in res.get('result', []):
                last_id = update['update_id']
                
                if 'callback_query' in update:
                    cb = update['callback_query']
                    chat_id = cb['message']['chat']['id']
                    cb_data = cb['data']
                    
                    if str(chat_id) != ADMIN_CHAT_ID: continue
                    
                    settings = load_settings()
                    
                    if cb_data == "cmd_bookings":
                        data = load_bookings()
                        if not data:
                            send_telegram("مفيش حجوزات لسه")
                        else:
                            msg = f"<b>الحجوزات - {len(data)} حجز</b>\n\n"
                            for b in data[::-1][:10]:
                                msg += f"<b>الاسم:</b> {b['name']}\n<b>الرقم:</b> {b['phone']}\n<b>الصف:</b> {b['grade']}\n<b>التاريخ:</b> {b['date']}\n<b>الوقت:</b> {b['time']}\n-------------------\n"
                            send_telegram(msg)
                            
                    elif cb_data == "menu_images":
                        kb = {"inline_keyboard": [
                            [{"text": "صورة الواجهة الرئيسية", "callback_data": "set_img_hero"}],
                            [{"text": "صورة قسم عن المستر", "callback_data": "set_img_about"}],
                            [{"text": "المعرض (صورة 1)", "callback_data": "set_img_gallery1"}, {"text": "المعرض (صورة 2)", "callback_data": "set_img_gallery2"}],
                            [{"text": "المعرض (صورة 3)", "callback_data": "set_img_gallery3"}, {"text": "المعرض (صورة 4)", "callback_data": "set_img_gallery4"}],
                            [{"text": "رجوع", "callback_data": "main_menu"}]
                        ]}
                        send_telegram("اختر الصورة التي تريد تغييرها (ستحتاج لإرسال رابط الصورة الجديد مباشرة):", kb)
                        
                    elif cb_data == "menu_texts":
                        kb = {"inline_keyboard": [
                            [{"text": "اسم السنتر / العنوان الرئيسي", "callback_data": "set_hero_title"}],
                            [{"text": "الوصف الرئيسي تحت الاسم", "callback_data": "set_hero_desc"}],
                            [{"text": "عنوان قسم (عن المستر)", "callback_data": "set_about_title"}],
                            [{"text": "وصف قسم (عن المستر)", "callback_data": "set_about_desc"}],
                            [{"text": "رجوع", "callback_data": "main_menu"}]
                        ]}
                        send_telegram("اختر النص الذي تريد تعديله:", kb)
                        
                    elif cb_data == "menu_prices":
                        kb = {"inline_keyboard": [
                            [{"text": "سعر الحصة الفردية", "callback_data": "set_price_single"}],
                            [{"text": "سعر باقة 4 حصص", "callback_data": "set_price_4_classes"}],
                            [{"text": "سعر باقة الشهر", "callback_data": "set_price_month"}],
                            [{"text": "رجوع", "callback_data": "main_menu"}]
                        ]}
                        send_telegram("اختر الباقة لتعديل سعرها:", kb)
                        
                    elif cb_data == "main_menu":
                        send_telegram("اهلا يا سيد اللعبة. إليك لوحة التحكم الخاصة بالموقع:", get_admin_keyboard())
                        
                    elif cb_data.startswith("set_"):
                        setting_key = cb_data.replace("set_", "")
                        admin_state[str(chat_id)] = setting_key
                        send_telegram(f"أرسل الآن القيمة أو الرابط الجديد لـ: {setting_key}")

                elif 'message' in update:
                    message = update['message']
                    chat_id = message.get('chat', {}).get('id')
                    text = message.get('text', '')
                    
                    if str(chat_id) != ADMIN_CHAT_ID: continue
                    
                    if str(chat_id) in admin_state and text not in ['/start', '/admin']:
                        key_to_update = admin_state[str(chat_id)]
                        settings = load_settings()
                        settings[key_to_update] = text
                        save_settings(settings)
                        
                        del admin_state[str(chat_id)]
                        send_telegram(f"تم تحديث {key_to_update} بنجاح في الموقع!", get_admin_keyboard())
                    else:
                        if text in ['/start', '/admin']:
                            send_telegram("اهلا يا سيد اللعبة. إليك لوحة التحكم الخاصة بالموقع من هنا مباشرة:", get_admin_keyboard())
        except: pass
        time.sleep(2)

@app.route('/', methods=['GET','POST'])
def home():
    settings = load_settings()
    already_booked = request.cookies.get('has_booked') == 'true'

    if request.method == 'POST':
        if already_booked:
            return make_response(render_template_string(HTML, already_booked=True, settings=settings))
            
        data = load_bookings()
        booking = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'grade': request.form['grade'],
            'date': request.form['date'],
            'note': request.form['note'],
            'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        data.append(booking)
        save_bookings(data)
        
        admin_msg = f"حجز جديد!\nالاسم: {booking['name']}\nالرقم: {booking['phone']}\nالصف: {booking['grade']}\nالتاريخ: {booking['date']}"
        threading.Thread(target=send_telegram, args=(admin_msg,)).start()
        
        resp = make_response(render_template_string(HTML, already_booked=True, settings=settings))
        resp.set_cookie('has_booked', 'true', max_age=31536000) 
        return resp

    return render_template_string(HTML, already_booked=already_booked, settings=settings)

if __name__ == '__main__':
    if TELEGRAM_TOKEN != "":
        threading.Thread(target=admin_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
