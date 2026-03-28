from flask import Flask, request, jsonify
import sqlite3
import uuid
from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)

# =========================
# JWT SETUP (IMPORTANT)
# =========================
app.config["JWT_SECRET_KEY"] = "change-this-secret-key"
jwt = JWTManager(app)

# =========================
# DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    # Payments table
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        provider TEXT,
        phone TEXT,
        amount REAL,
        status TEXT,
        transaction_id TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# INITIATE PAYMENT
# =========================
@app.route("/pay", methods=["POST"])
@jwt_required()
def pay():
    user = get_jwt_identity()
    data = request.json

    provider = data.get("provider")   # mpesa / airtel / tigo / halopesa
    phone = data.get("phone")
    amount = data.get("amount")

    transaction_id = str(uuid.uuid4())

    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO payments (
            username, provider, phone, amount, status, transaction_id, timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user,
        provider,
        phone,
        amount,
        "PENDING",
        transaction_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Payment started",
        "transaction_id": transaction_id,
        "status": "PENDING"
    })

# =========================
# CALLBACK (FOR PROVIDERS)
# =========================
@app.route("/payment/callback", methods=["POST"])
def payment_callback():
    data = request.json

    transaction_id = data.get("transaction_id")
    status = data.get("status")  # SUCCESS / FAILED

    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    c.execute("""
        UPDATE payments
        SET status = ?
        WHERE transaction_id = ?
    """, (status, transaction_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Payment updated"})

# =========================
# CHECK PAYMENT STATUS
# =========================
@app.route("/payment/status", methods=["GET"])
@jwt_required()
def payment_status():
    user = get_jwt_identity()

    conn = sqlite3.connect("traffic.db")
    c = conn.cursor()

    c.execute("""
        SELECT provider, amount, status, transaction_id, timestamp
        FROM payments
        WHERE username = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user,))

    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"status": "NO_PAYMENT"})

    return jsonify({
        "provider": row[0],
        "amount": row[1],
        "status": row[2],
        "transaction_id": row[3],
        "timestamp": row[4]
    })

# =========================
# START TEST SERVER
# =========================
if __name__ == "__main__":
    print("💰 Payment System Running...")
    app.run(port=5001, debug=True)