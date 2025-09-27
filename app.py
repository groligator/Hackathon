from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timecapsule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------
# Database Model
# -----------------------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    open_date_iso = db.Column(db.String, nullable=False)  # UTC ISO string with Z
    created_at_iso = db.Column(db.String, nullable=False)  # UTC ISO string with Z

    def is_open(self):
        now_utc = datetime.now(timezone.utc)
        open_dt = datetime.fromisoformat(self.open_date_iso.replace('Z', '+00:00'))
        # Ensure open_dt is timezone-aware
        if open_dt.tzinfo is None:
            open_dt = open_dt.replace(tzinfo=timezone.utc)
        return now_utc >= open_dt

# -----------------------
# Routes
# -----------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        content = request.form['content']
        open_date_str = request.form['open_date']  # YYYY-MM-DD

        # Convert date to UTC ISO string at midnight with Z
        open_date = datetime.strptime(open_date_str, '%Y-%m-%d')
        open_date_iso = datetime.combine(open_date.date(), datetime.min.time(), tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')

        # Current UTC time as ISO string with Z
        created_at_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        message = Message(
            username=username,
            content=content,
            open_date_iso=open_date_iso,
            created_at_iso=created_at_iso
        )
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('messages'))

    return render_template('submit.html')


@app.route('/messages')
def messages():
    all_messages = Message.query.order_by(Message.id.desc()).all()  # newest first
    now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    unlocked_messages = []
    locked_messages = []

    for msg in all_messages:
        if msg.is_open():
            unlocked_messages.append(msg)
        else:
            locked_messages.append(msg)

    return render_template('messages.html',
                           unlocked_messages=unlocked_messages,
                           locked_messages=locked_messages,
                           now_iso=now_iso)


# -----------------------
# Main
# -----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
