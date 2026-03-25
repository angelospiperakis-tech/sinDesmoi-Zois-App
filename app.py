from flask import send_file
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.message import EmailMessage
import ssl

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
db = SQLAlchemy(app)

# ---------------- DATABASE ----------------

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    area = db.Column(db.String(10))
    email = db.Column(db.String(100))
    code = db.Column(db.String(100))

# ---------------- EMAIL (ΔΟΥΛΕΥΕΙ ΣΙΓΟΥΡΑ) ----------------

EMAIL = "sindesmoizois@gmail.com"
PASS = "zudb bnvd byis nmkb"

def send_email(to_email, code, name):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Ο προσωπικός σας κωδικός"
        msg["From"] = EMAIL
        msg["To"] = to_email

        msg.set_content(f"""
Αγαπητέ/ή {name},

Ο προσωπικός σας κωδικός είναι:

{code}

Με εκτίμηση,
ΣύνΔεσμοί Ζωής
        """)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL, PASS)
            server.send_message(msg)

        print("EMAIL OK")

    except Exception as e:
        print("EMAIL ERROR:", e)

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/create", methods=["POST"])
def create():
    data = request.json

    name = data["name"].upper()
    surname = data["surname"].upper()
    area = data["area"].upper()
    email = data["email"]

    initials = name[:2] + surname[:2]
    today = datetime.now().strftime("%d%m")

    count = Client.query.count()
    number = str(count + 1).zfill(3)

    code = f"ΦΑΣΜΑ-{area}-{initials}-{today}-{number}"

    client = Client(
        name=name,
        surname=surname,
        area=area,
        email=email,
        code=code
    )

    db.session.add(client)
    db.session.commit()

    send_email(email, code, name)

    return jsonify({"code": code})

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):
    try:
        c = Client.query.get(id)

        if not c:
            return jsonify({"error": "not found"}), 404

        db.session.delete(c)
        db.session.commit()

        print("DELETED:", id)

        return jsonify({"ok": True})

    except Exception as e:
        print("DELETE ERROR:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/clients")
def clients():
    data = []
    for c in Client.query.all():
        data.append({
            "id": c.id,
            "name": c.name,
            "surname": c.surname,
            "area": c.area,
            "email": c.email,
            "code": c.code
        })
    return jsonify(data)

# ---------------- INIT ----------------

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)