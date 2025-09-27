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
    open_date = db.Column(db.DateTime, nullable=False)  # UTC-aware
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # UTC-aware

    def is_open(self):
        now_utc = datetime.now(timezone.utc)
        open_date_aware = self.open_date
        if self.open_date.tzinfo is None:
            open_date_aware = self.open_date.replace(tzinfo=timezone.utc)
        return now_utc >= open_date_aware

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
        open_date_str = request.form['open_date']  # format: YYYY-MM-DD

        # Convert to UTC-aware datetime at midnight
        open_date = datetime.strptime(open_date_str, '%Y-%m-%d')
        open_date = open_date.replace(tzinfo=timezone.utc)

        message = Message(username=username, content=content, open_date=open_date)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('messages'))

    return render_template('submit.html')


@app.route('/messages')
def messages():
    all_messages = Message.query.order_by(Message.created_at.desc()).all()
    now_utc = datetime.now(timezone.utc)

    unlocked_messages = []
    locked_messages = []

    # Precompute UTC ISO strings for the template
    for msg in all_messages:
        msg.created_at_iso = msg.created_at.astimezone(timezone.utc).isoformat()
        msg.open_date_iso = msg.open_date.astimezone(timezone.utc).isoformat()
        if msg.is_open():
            unlocked_messages.append(msg)
        else:
            locked_messages.append(msg)

    now_iso = now_utc.isoformat()

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
