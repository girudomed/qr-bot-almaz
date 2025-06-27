import os
import io
import time
import json
import base64
import hmac
import hashlib
from datetime import datetime, timezone, timedelta
from flask import Flask, request, render_template_string, send_file
from dotenv import load_dotenv
import qrcode
from supabase import create_client, Client

# Московское время (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))

def get_moscow_time():
    """Получить текущее время в Москве"""
    return datetime.now(MOSCOW_TZ)

def get_moscow_timestamp():
    """Получить timestamp московского времени"""
    return int(get_moscow_time().timestamp())

# Загрузка переменных окружения
load_dotenv()

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
QR_SECRET = os.environ.get("QR_SECRET")

if not (SUPABASE_URL and SUPABASE_KEY and QR_SECRET):
    raise Exception("Укажите все переменные окружения: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, QR_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Получение списка филиалов из таблицы 'branches' через Supabase API
def get_branches():
    try:
        res = supabase.table("branches").select("*").execute()
        if res.data:
            print(f"Получено филиалов: {len(res.data)}", flush=True)
            return res.data
        print("Филиалы не найдены", flush=True)
        return []
    except Exception as e:
        import traceback; traceback.print_exc()
        print("Ошибка при получении филиалов через Supabase API:", e, flush=True)
        return []

# Генерация подписи для QR (HMAC-SHA256)
def generate_signature(branch_id, time_window):
    msg = f"{branch_id}:{time_window}".encode()
    secret = QR_SECRET.encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()

# Генерация base64-кодированной строки для QR
def generate_qr_payload(branch_id, branch_name):
    timestamp = get_moscow_timestamp()
    time_window = timestamp // 30  # Окно 30 секунд
    expires = timestamp + 60
    signature = generate_signature(branch_id, time_window)
    payload = {
        "branch_id": branch_id,
        "branch_name": branch_name,
        "timestamp": time_window,
        "expires": expires,
        "signature": signature,
    }
    json_str = json.dumps(payload, ensure_ascii=False)
    base64_str = base64.urlsafe_b64encode(json_str.encode()).decode()
    return base64_str

@app.route("/", methods=["GET"])
def index():
    branches = get_branches()
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <title>QR для сотрудников</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; padding: 2em; }
                .container { background: #fff; padding: 2em; max-width: 400px; margin: auto; border-radius: 16px; box-shadow: 0 0 10px #bbb; }
                select, button { padding: 0.6em 1em; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 1em; width: 100%; }
                img { display: block; margin: 1.5em auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Генерация QR-кода</h2>
                <form method="get" action="/qr">
                    <label>Выберите филиал:</label>
                    <select name="branch_id" required>
                        {% for branch in branches %}
                            <option value="{{branch['id']}}">{{branch['name']}}</option>
                        {% endfor %}
                    </select>
                    <button type="submit">Показать QR</button>
                </form>
            </div>
        </body>
        </html>
        """, branches=branches
    )

@app.route("/qr", methods=["GET"])
def qr():
    branch_id = request.args.get("branch_id", type=int)
    if not branch_id:
        return "Не выбран филиал", 400
    branches = get_branches()
    branch = next((b for b in branches if b["id"] == branch_id), None)
    if not branch:
        return "Филиал не найден", 404
    qr_data = generate_qr_payload(branch_id, branch["name"])
    qr_full = f"/qr_{qr_data}"

    # Генерируем картинку QR
    qr_img = qrcode.make(qr_full)
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)

    # HTML для отображения QR-кода с автообновлением
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <title>QR-код для {{branch['name']}}</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f4; text-align: center; padding: 2em; }
                .container { background:#fff; display:inline-block; padding:2em; border-radius:16px; box-shadow: 0 0 10px #bbb; }
                .timer { font-size: 18px; color: #007bff; margin: 10px 0; }
                .expired { color: #dc3545; }
                img { margin: 1.5em 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Филиал: {{branch['name']}}</h2>
                <div id="qr-container">
                    <img id="qr-image" src="/qr_image?branch_id={{branch['id']}}&t=" alt="QR-код" width="300"/>
                </div>
                <div class="timer">
                    <span id="timer">Обновление через: <span id="countdown">30</span> сек</span>
                </div>
                <p>QR-код действителен 1 минуту</p>
                <a href="/">Назад</a>
            </div>
            
            <script>
                let countdown = 30;
                let timerElement = document.getElementById('countdown');
                let qrImage = document.getElementById('qr-image');
                let branchId = {{branch['id']}};
                
                function updateQR() {
                    // Обновляем QR-код с новым timestamp
                    qrImage.src = '/qr_image?branch_id=' + branchId + '&t=' + Date.now();
                    countdown = 30;
                }
                
                function updateTimer() {
                    timerElement.textContent = countdown;
                    countdown--;
                    
                    if (countdown < 0) {
                        updateQR();
                    }
                }
                
                // Обновляем таймер каждую секунду
                setInterval(updateTimer, 1000);
                
                // Обновляем QR каждые 30 секунд
                setInterval(updateQR, 30000);
            </script>
        </body>
        </html>
        """, branch=branch
    )

@app.route("/qr_image")
def qr_image():
    # Поддержка старого формата (data) и нового (branch_id)
    data = request.args.get("data", "")
    branch_id = request.args.get("branch_id", type=int)
    
    if data:
        # Старый формат - используем готовые данные
        qr_full = f"/qr_{data}"
    elif branch_id:
        # Новый формат - генерируем QR по branch_id
        branches = get_branches()
        branch = next((b for b in branches if b["id"] == branch_id), None)
        if not branch:
            return "Филиал не найден", 404
        qr_data = generate_qr_payload(branch_id, branch["name"])
        qr_full = f"/qr_{qr_data}"
    else:
        return "Нет данных для QR", 400
    
    qr_img = qrcode.make(qr_full)
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == "__main__":
    app.run("0.0.0.0", 8080, debug=True)
