from flask import Flask, render_template_string, request, make_response
import json, os, datetime, threading, time
import requests

app = Flask(__name__)
BOOKINGS_FILE = 'bookings.json'
PRICE = 40

TELEGRAM_TOKEN = os.environ.get("8801743115:AAGN2S0DwR5lSMwYMjmsxLyD4E8LJ62mdZI")
ADMIN_CHAT_ID = os.environ.get("7728398907")

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        try: 
            with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: 
            return []
    return []

def save_bookings(data):
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not ADMIN_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try: 
        requests.post(url, data=data, timeout=10)
    except: 
        pass

HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>سيد اللعبة - مستر الرياضيات</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
:root{--pink:#FF2D92;--pink-dark:#C2185B;--black:#000;--card:#111111}
*{margin:0;padding:0;font-family:'Cairo',tahoma;box-sizing:border-box;scroll-behavior:smooth}
body{background:var(--black);color:#fff;overflow-x:hidden}

nav{position:fixed;top:0;width:100%;background:rgba(0,0,0,0.9);padding:15px 20px;display:flex;justify-content:space-between;z-index:100;border-bottom:2px solid var(--pink)}
nav a{color:#fff;text-decoration:none;margin:0 10px;font-weight:700;transition:0.3s}
nav a:hover{color:var(--pink)}

.hero{min-height:100vh;background:linear-gradient(135deg, rgba(255,45,146,0.3), rgba(0,0,0,0.9)),url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=2070') center/cover; display:flex;align-items:center;justify-content:center;text-align:center;padding:80px 20px}
.hero h1{font-size:3.5rem;font-weight:900;color:var(--pink);text-shadow:0 0 20px var(--pink)}
.hero p{font-size:1.3rem;margin:20px 0;color:#eee}

.btn{background:linear-gradient(45deg, var(--pink), var(--pink-dark));color:#fff;padding:14px 40px;border:none;border-radius:50px;font-size:17px;font-weight:900;cursor:pointer;text-decoration:none;display:inline-block;box-shadow:0 0 25px rgba(255,45,146,0.5);transition:0.3s}
.btn:hover{transform:scale(1.05);box-shadow:0 0 40px rgba(255,45,146,0.8)}

section{padding:70px 20px;max-width:1300px;margin:auto}
.section-title{text-align:center;font-size:2.5rem;margin-bottom:40px;color:var(--pink);text-shadow:0 0 15px var(--pink)}

.form-container{background:var(--card);padding:40px 25px;border-radius:20px;max-width:650px;margin:auto;border:2px solid var(--pink);box-shadow:0 0 30px rgba(255,45,146,0.3)}
input,select,textarea{width:100%;padding:14px;margin-bottom:15px;border-radius:12px;border:2px solid #333;background:#0a0a0a;color:#fff;font-size:16px;text-align:right;transition:0.3s}
input:focus,select:focus,textarea:focus{border-color:var(--pink);outline:none;box-shadow:0 0 15px rgba(255,45,146,0.5)}

.success-box{padding:25px;background:rgba(255,45,146,0.1);border:2px solid var(--pink);border-radius:15px;color:var(--pink);font-weight:bold;font-size:1.3rem;text-align:center}

footer{text-align:center;padding:30px;background:#000;border-top:2px solid var(--pink);color:#aaa}
</style></head><body>

<nav>
    <div style="font-weight:900;color:var(--pink);font-size:22px"><i class="fa-solid fa-crown"></i> سيد اللعبة</div>
    <div><a href="#home">الرئيسية</a><a href="#book">الحجز</a></div>
</nav>

<section class="hero" id="home">
    <div>
        <h1>سيد اللعبة</h1>
        <p>مستر الرياضيات اللي هيقفل معاك المادة 👑</p>
        {% if already_booked %}
            <a href="#book" class="btn"><i class="fa-solid fa-clipboard-check"></i> حالة الحجز</a>
        {% else %}
            <a href="#book" class="btn"><i class="fa-solid fa-calendar-days"></i> احجز بـ 40 جنيه</a>
        {% endif %}
    </div>
</section>

<section id="book">
    <h2 class="section-title">احجز مكانك</h2>
    <div class="form-container">
        {% if already_booked %}
            <div class="success-box">
                <i class="fa-solid fa-circle-check"></i><br>
                تم الحجز بنجاح سابقاً!<br>
                هنتواصل معاك واتساب
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
                <textarea name="note" placeholder="ملاحظات"></textarea>
                <button class="btn" style="width:100%"><i class="fa-solid fa-check"></i> تأكيد الحجز</button>
            </form>
        {% endif %}
    </div>
</section>

<footer>© 2026 سيد اللعبة | تصميم وردي × اسود</footer>
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
                            send_telegram("مفيش حجوزات لسه")
                            continue
                        msg = f"<b>الحجوزات - {len(data)} حجز</b>\n\n"
                        for b in data[::-1][:10]:
                            msg += f"<b>الاسم:</b> {b['name']}\n<b>الرقم:</b> {b['phone']}\n<b>الصف:</b> {b['grade']}\n<b>التاريخ:</b> {b['date']}\n-------------------\n"
                        send_telegram(msg)
        except: pass
        time.sleep(2)

@app.route('/', methods=['GET','POST'])
def home():
    already_booked = request.cookies.get('has_booked') == 'true'
    if request.method == 'POST':
        if already_booked:
            return render_template_string(HTML, already_booked=True)
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
        admin_msg = f"<b>حجز جديد!</b>\n<b>الاسم:</b> {booking['name']}\n<b>الرقم:</b> {booking['phone']}\n<b>الصف:</b> {booking['grade']}\n<b>التاريخ:</b> {booking['date']}"
        threading.Thread(target=send_telegram, args=(admin_msg,)).start()
        resp = make_response(render_template_string(HTML, already_booked=True))
        resp.set_cookie('has_booked', 'true', max_age=31536000) 
        return resp
    return render_template_string(HTML, already_booked=already_booked)

if __name__ == '__main__':
    if TELEGRAM_TOKEN and ADMIN_CHAT_ID:
        threading.Thread(target=admin_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)