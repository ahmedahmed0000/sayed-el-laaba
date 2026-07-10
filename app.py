from flask import Flask, render_template_string, request, make_response
import json, os, datetime, threading, time
import requests

app = Flask(__name__)
BOOKINGS_FILE = 'bookings.json'
SETTINGS_FILE = 'settings.json' # ملف جديد عشان الصور
PRICE = 40  

# اقرا من Environment Variables بتاعت Render
TELEGRAM_TOKEN = os.environ.get("8801743115:AAGN2S0DwR5lSMwYMjmsxLyD4E8LJ62mdZI")
ADMIN_CHAT_ID = os.environ.get("7728398907")

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        try: return json.load(open(BOOKINGS_FILE, encoding='utf-8'))
        except: return []
    return []

def save_bookings(data):
    json.dump(data, open(BOOKINGS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

# دوال جديدة للتحكم في الصور
def load_settings():
    default = {
        "hero_bg": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=2070",
        "about_img": "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=2032",
        "gallery": [
            "https://images.unsplash.com/photo-1580582932707-520aed937b7b?q=80&w=1932",
            "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=2022",
            "https://images.unsplash.com/photo-1599058917212-d750089bc07e?q=80&w=2070",
            "https://images.unsplash.com/photo-1562774053-701939374585?q=80&w=2071"
        ]
    }
    if os.path.exists(SETTINGS_FILE):
        try: 
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return {**default, **json.load(f)} # دمج مع الافتراضي
        except: return default
    return default

def save_settings(data):
    json.dump(data, open(SETTINGS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not ADMIN_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try: requests.post(url, data=data, timeout=10)
    except: pass

# HTML بقى ديناميك عشان الصور
def get_html(settings):
    return f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8">
<title>سيد اللعبة - مستر الرياضيات</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
:root{{--gold:#FFD700;--dark:#0a0a0a;--card:#111}}
*{margin:0;padding:0;font-family:'Cairo',tahoma;box-sizing:border-box;scroll-behavior:smooth}
body{{background:var(--dark);color:#fff}}

@keyframes glow {{0%,100%{{box-shadow:0 0 20px var(--gold)}}50%{{box-shadow:0 0 40px var(--gold)}}}}
nav{{position:fixed;top:0;width:100%;background:rgba(0, 0, 0, 0.85);backdrop-filter:blur(10px);padding:15px 20px;display:flex;justify-content:space-between;z-index:100}}
nav a{{color:#fff;text-decoration:none;margin:0 8px;font-weight:700}}
.hero{{min-height:100vh;background:linear-gradient(rgba(0,0,0,0.6),rgba(0,0,0,0.8)),url('{settings['hero_bg']}') center/cover; display:flex;align-items:center;justify-content:center;text-align:center;padding:80px 20px}}
.hero h1{{font-size:3rem;font-weight:900;color:var(--gold);animation:glow 2s infinite}}
.btn{{background:var(--gold);color:#000;padding:12px 35px;border:none;border-radius:50px;font-size:16px;font-weight:900;cursor:pointer;text-decoration:none;display:inline-block}}
section{{padding:60px 20px;max-width:1300px;margin:auto}}
.section-title{{text-align:center;font-size:2.2rem;margin-bottom:40px;color:var(--gold)}}
.about{{display:flex;gap:30px;align-items:center;flex-wrap:wrap;justify-content:center}}
.about img{{width:100%;max-width:400px;height:auto;border-radius:20px;animation:glow 2s infinite}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px}}
.gallery img{{width:100%;height:220px;object-fit:cover;border-radius:15px;transition:0.4s}}
.gallery img:hover{{transform:scale(1.05)}}
.form-container{{background:var(--card);padding:40px 20px;border-radius:20px;max-width:650px;margin:auto;border:2px solid #333}}
input,select,textarea{{width:100%;padding:12px;margin-bottom:15px;border-radius:10px;border:2px solid #333;background:#1a1a1a;color:#fff;font-size:16px;text-align:right;}}
.success-box{{padding:20px;color:#00ff88;font-weight:bold;font-size:1.3rem;text-align:center}}
footer{{text-align:center;padding:25px;background:#000;color:#aaa}}
</style></head><body>

<nav>
    <div style="font-weight:900;color:var(--gold);font-size:20px"><i class="fa-solid fa-crown"></i> سيد اللعبة</div>
    <div><a href="#home">الرئيسية</a><a href="#about">عن المستر</a><a href="#gallery">صورنا</a><a href="#book">الحجز</a></div>
</nav>

<section class="hero" id="home">
    <div>
        <h1>سيد اللعبة</h1>
        <p>مستر الرياضيات اللي هيخليك تقفل المادة</p>
        {{% if already_booked %}}
            <a href="#book" class="btn"><i class="fa-solid fa-clipboard-check"></i> تم الحجز</a>
        {{% else %}}
            <a href="#book" class="btn"><i class="fa-solid fa-calendar-days"></i> احجز بـ 40 جنيه</a>
        {{% endif %}}
    </div>
</section>

<section id="about">
    <h2 class="section-title">عن المستر</h2>
    <div class="about">
        <img src="{settings['about_img']}">
        <div><h3 style="color:var(--gold)">خبرة 10 سنين في اللعبة</h3><p>مع المkستر الرياضيات هتبقى لعبة</p></div>
    </div>
</section>

<section id="gallery">
    <h2 class="section-title">صور من السنتر</h2>
    <div class="gallery">
        {''.join([f'<img src="{img}">' for img in settings['gallery']])}
    </div>
</section>

<section id="book">
    <h2 class="section-title">الحجز</h2>
    <div class="form-container">
        {{% if already_booked %}}
            <div class="success-box"><i class="fa-solid fa-circle-check"></i><br>تم الحجز بنجاح سابقاً!</div>
        {{% else %}}
            <form method="POST">
                <input name="name" placeholder="الاسم الكامل" required>
                <input name="phone" placeholder="رقم الواتساب" required>
                <select name="grade" required><option value="">اختر الصف</option><option>اولى ثانوي</option><option>تانية ثانوي</option><option>تالتة ثانوي</option></select>
                <input type="date" name="date" required>
                <button class="btn" style="width:100%"> تأكيد الحجز</button>
            </form>
        {{% endif %}}
    </div>
</section>
<footer>© 2026 سيد اللعبة</footer>
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
                    settings = load_settings()
                    # اوامر الصور الجديدة
                    if text.startswith('/setbg '):
                        settings['hero_bg'] = text.replace('/setbg ', '')
                        save_settings(settings)
                        send_telegram("تم تغيير صورة الخلفية ✅")
                    elif text.startswith('/setabout '):
                        settings['about_img'] = text.replace('/setabout ', '')
                        save_settings(settings)
                        send_telegram("تم تغيير صورة عن المستر ✅")
                    elif text.startswith('/setgallery '):
                        links = text.replace('/setgallery ', '').split(',')
                        settings['gallery'] = [l.strip() for l in links]
                        save_settings(settings)
                        send_telegram(f"تم تغيير {len(links)} صور في الجاليري ✅")
                    elif text == '/bookings':
                        data = load_bookings()
                        if not data: send_telegram("مفيش حجوزات لسه"); continue
                        msg = f"<b>الحجوزات - {len(data)} حجز</b>\n\n"
                        for b in data[::-1][:10]: msg += f"<b>الاسم:</b> {b['name']}\n<b>الرقم:</b> {b['phone']}\n-------------------\n"
                        send_telegram(msg)
                    elif text == '/help':
                        send_telegram("<b>اوامر الادمن:</b>\n`/bookings` - عرض الحجوزات\n`/setbg رابط` - تغيير خلفية الرئيسية\n`/setabout رابط` - تغيير صورة عن المستر\n`/setgallery رابط1,رابط2,رابط3` - تغيير صور الجاليري")
        except: pass
        time.sleep(2)

@app.route('/', methods=['GET','POST'])
def home():
    settings = load_settings()
    already_booked = request.cookies.get('has_booked') == 'true'
    if request.method == 'POST':
        if already_booked: return render_template_string(get_html(settings), already_booked=True)
        data = load_bookings()
        booking = {'name': request.form['name'], 'phone': request.form['phone'], 'grade': request.form['grade'], 'date': request.form['date'], 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
        data.append(booking)
        save_bookings(data)
        threading.Thread(target=send_telegram, args=(f"<b>حجز جديد!</b>\n<b>الاسم:</b> {booking['name']}",)).start()
        resp = make_response(render_template_string(get_html(settings), already_booked=True))
        resp.set_cookie('has_booked', 'true', max_age=31536000) 
        return resp
    return render_template_string(get_html(settings), already_booked=already_booked)

if __name__ == '__main__':
    if TELEGRAM_TOKEN and ADMIN_CHAT_ID:
        threading.Thread(target=admin_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)