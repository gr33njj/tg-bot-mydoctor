# admin.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
import requests
from models import SessionLocal, init_db, User, Message
from datetime import datetime, timedelta

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "changeme")
FLASK_SECRET = os.getenv("FLASK_SECRET") or os.urandom(24).hex()

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN not set in .env")

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__, template_folder="templates")
app.secret_key = FLASK_SECRET

# ensure db
init_db()

def send_telegram_message(tg_id, text):
    url = f"{API_BASE}/sendMessage"
    payload = {"chat_id": tg_id, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception:
        return False

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u == ADMIN_USER and p == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        flash("Неверные учетные данные", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

def require_login():
    if not session.get("admin"):
        return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    db = SessionLocal()
    total = db.query(User).count()
    now = datetime.utcnow()
    active_day = db.query(User).filter(User.last_active >= now - timedelta(days=1)).count()
    active_week = db.query(User).filter(User.last_active >= now - timedelta(days=7)).count()
    active_month = db.query(User).filter(User.last_active >= now - timedelta(days=30)).count()
    users = db.query(User).order_by(User.joined_at.desc()).limit(200).all()
    messages = db.query(Message).order_by(Message.created_at.desc()).limit(200).all()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "broadcast":
            text = request.form.get("broadcast_text", "").strip()
            if not text:
                flash("Введите текст рассылки", "warning")
            else:
                count = 0
                for u in db.query(User).all():
                    ok = send_telegram_message(u.tg_id, text)
                    if ok:
                        m = Message(user_id=u.tg_id, direction="out", text=text)
                        db.add(m)
                        count += 1
                db.commit()
                flash(f"Отправлено {count} сообщений", "success")
            return redirect(url_for("dashboard"))

        if action == "reply":
            tg_id = int(request.form.get("reply_to"))
            text = request.form.get("reply_text", "").strip()
            if text:
                ok = send_telegram_message(tg_id, text)
                if ok:
                    m = Message(user_id=tg_id, direction="out", text=text)
                    db.add(m)
                    db.commit()
                    flash("Ответ отправлен", "success")
                else:
                    flash("Ошибка отправки", "danger")
            else:
                flash("Введите текст ответа", "warning")
            return redirect(url_for("dashboard"))

    return render_template("admin.html", total=total, active_day=active_day,
                           active_week=active_week, active_month=active_month,
                           users=users, messages=messages)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
