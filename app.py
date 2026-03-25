from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

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

# ---------------- EMAIL ----------------

EMAIL = os.getenv("EMAIL")
PASS = os.getenv("PASS")

def send_email(to_email, code, name):
    try:
        html = f"""
        <html>
        <body style="font-family: Arial; background:#f4f4f4; padding:20px;">
        <div style="background:white; padding:20px; border-radius:10px;">
        <h2 style="color:#4facfe;">ΣύνΔεσμοί Ζωής</h2>
        <p>Αγαπητέ/ή <b>{name}</b>,</p>
        <p>Ο κωδικός σας:</p>
        <div style="background:#4facfe;color:white;padding:10px;border-radius:5px;">
        {code}
        </div>
        <p>Με εκτίμηση,<br>ΣύνΔεσμοί Ζωής</p>
        </div>
        </body>
        </html>
        """

        msg = MIMEText(html, "html")
        msg["Subject"] = "Ο κωδικός σας"
        msg["From"] = EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL, PASS)
        server.send_message(msg)
        server.quit()

    except:
        print("Email failed")

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

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):
    c = Client.query.get(id)
    if c:
        db.session.delete(c)
        db.session.commit()
    return jsonify({"ok": True})

# ---------------- INIT ----------------

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)