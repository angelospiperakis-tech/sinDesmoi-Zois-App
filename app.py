from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
db = SQLAlchemy(app)

# ------------------ DATABASE ------------------

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    area = db.Column(db.String(10))
    email = db.Column(db.String(100))
    code = db.Column(db.String(100))

# ------------------ ENV VARIABLES ------------------

EMAIL = os.getenv("EMAIL")
PASS = os.getenv("PASS")

# ------------------ EMAIL ------------------

def send_email(to_email, code, name):
    html = f"""
    <html>
    <body style="font-family: Arial; background-color:#f4f4f4; padding:20px;">
    <div style="max-width:500px; margin:auto; background:white; padding:25px; border-radius:10px;">
    
    <h2 style="color:#4facfe; text-align:center;">
    ΣύνΔεσμοί Ζωής
    </h2>

    <p>Αγαπητέ/ή <b>{name}</b>,</p>

    <p>Ο προσωπικός σας κωδικός είναι:</p>

    <div style="background:#4facfe; color:white; padding:15px; border-radius:8px; text-align:center; font-size:18px;">
    🔑 {code}
    </div>

    <p style="margin-top:15px;">
    Παρακαλούμε χρησιμοποιήστε τον στις κρατήσεις σας.
    </p>

    <hr>

    <p style="text-align:center; font-size:12px; color:gray;">
    Με εκτίμηση,<br>
    ΣύνΔεσμοί Ζωής
    </p>

    </div>
    </body>
    </html>
    """

    msg = MIMEText(html, "html")
    msg["Subject"] = "Ο προσωπικός σας κωδικός"
    msg["From"] = EMAIL
    msg["To"] = to_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, PASS)
    server.send_message(msg)
    server.quit()

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

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
def get_clients():
    clients = Client.query.all()

    data = []
    for c in clients:
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
def delete_client(id):
    client = Client.query.get(id)

    if not client:
        return jsonify({"error": "Not found"}), 404

    db.session.delete(client)
    db.session.commit()

    return jsonify({"message": "Deleted"})

# ------------------ RUN ------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)