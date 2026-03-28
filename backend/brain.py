from flask import Flask, request, jsonify
import requests
import base64
import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity, create_access_token
)

from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

# =========================
# INIT
# =========================
load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "secret")

jwt = JWTManager(app)
CORS(app)

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        phone TEXT UNIQUE
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY,
        phone TEXT,
        provider TEXT,
        amount REAL,
        status TEXT,
        tx_id TEXT UNIQUE,
        expiry TEXT,
        timestamp TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# =========================
# SAVE PAYMENT (SUBSCRIPTION)
# =========================
def save_payment(phone, amount, status, provider, tx_id):
    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    # 1000 = 1 day
    days = int(amount) // 1000
    if days < 1:
        days = 1

    expiry_date = datetime.now() + timedelta(days=days)

    try:
        c.execute("""
            INSERT INTO payments VALUES(NULL,?,?,?,?,?,?,?)
        """, (
            phone,
            provider,
            amount,
            status,
            tx_id,
            expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()

        print("✅ ACTIVE UNTIL:", expiry_date)

    except:
        print("⚠️ Duplicate transaction blocked")

    conn.close()

# =========================
# CHECK SUBSCRIPTION
# =========================
def check_payment(phone):
    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    c.execute("""
        SELECT expiry FROM payments
        WHERE phone=? AND status='SUCCESS'
        ORDER BY id DESC LIMIT 1
    """, (phone,))

    row = c.fetchone()
    conn.close()

    if not row:
        return False

    expiry = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")

    if datetime.now() > expiry:
        return False

    return True

# =========================
# REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    d = request.json

    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO users VALUES(NULL,?,?,?)
        """, (
            d["username"],
            generate_password_hash(d["password"]),
            d["phone"]
        ))
        conn.commit()
    except:
        return jsonify({"msg": "User already exists"}), 400

    conn.close()
    return jsonify({"msg": "Registered successfully"})

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    d = request.json

    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    c.execute("""
        SELECT password, phone FROM users WHERE username=?
    """, (d["username"],))

    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user[0], d["password"]):
        return jsonify({
            "token": create_access_token(identity=user[1])
        })

    return jsonify({"msg": "Invalid credentials"}), 401

# =========================
# MPESA TOKEN
# =========================
def get_token():
    key = os.getenv("MPESA_CONSUMER_KEY")
    secret = os.getenv("MPESA_CONSUMER_SECRET")

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    res = requests.get(url, auth=(key, secret))
    return res.json()["access_token"]

# =========================
# STK PUSH
# =========================
def stk_push(phone, amount):
    token = get_token()

    shortcode = os.getenv("MPESA_SHORTCODE")
    passkey = os.getenv("MPESA_PASSKEY")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    password = base64.b64encode(
        (shortcode + passkey + timestamp).encode()
    ).decode()

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": os.getenv("CALLBACK_URL"),
        "AccountReference": "TRAFFIC_AI",
        "TransactionDesc": "Subscription Payment"
    }

    return requests.post(url, json=payload, headers=headers).json()

# =========================
# PAY (LOCKED USER PHONE)
# =========================
@app.route("/pay", methods=["POST"])
@jwt_required()
def pay():
    phone = get_jwt_identity()
    amount = request.json["amount"]

    res = stk_push(phone, amount)

    return jsonify({
        "msg": "STK PUSH SENT",
        "phone": phone,
        "response": res
    })

# =========================
# SECURE CALLBACK
# =========================
@app.route("/payment/callback", methods=["POST"])
def callback():
    data = request.json

    if not data or "Body" not in data:
        return jsonify({"msg": "invalid"}), 400

    try:
        cb = data["Body"]["stkCallback"]

        if cb.get("ResultCode") != 0:
            return jsonify({"msg": "failed"}), 200

        items = cb.get("CallbackMetadata", {}).get("Item", [])

        phone = None
        amount = None
        receipt = None

        for item in items:
            if item["Name"] == "PhoneNumber":
                phone = str(item["Value"])
            elif item["Name"] == "Amount":
                amount = float(item["Value"])
            elif item["Name"] == "MpesaReceiptNumber":
                receipt = item["Value"]

        if not phone or not amount or not receipt:
            return jsonify({"msg": "missing fields"}), 400

        save_payment(
            phone,
            amount,
            "SUCCESS",
            "MPESA",
            receipt
        )

        print("💰 PAYMENT VERIFIED:", phone, amount)

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"msg": "error"}), 500

    return jsonify({"msg": "ok"})

# =========================
# PROTECTED ROUTE
# =========================
@app.route("/data")
@jwt_required()
def protected():
    phone = get_jwt_identity()

    if not check_payment(phone):
        return jsonify({
            "msg": "SUBSCRIPTION EXPIRED ❌"
        }), 403

    return jsonify({
        "msg": "ACCESS GRANTED ✅",
        "phone": phone
    })

# =========================
# RUN LOCAL
# =========================
if __name__ == "__main__":
    print("🚀 SYSTEM RUNNING LOCAL")
    app.run(host="0.0.0.0", port=10000)