from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timecapsule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    content = db.Column(db.Text)
    open_date = db.Column(db.Date)  # user only selects date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_open(self):
        # Return True if today >= open_date
        return date.today() >= self.open_date

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        content = request.form['content']
        open_date_str = request.form['open_date']  # e.g., "2025-09-27"
        open_date = datetime.strptime(open_date_str, '%Y-%m-%d').date()

        message = Message(username=username, content=content, open_date=open_date)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('messages'))

    return render_template('submit.html')

@app.route('/messages')
def messages():
    all_messages = Message.query.all()
    # Current datetime to display "opened on"
    now = datetime.now()  # datetime object
    return render_template('messages.html', messages=all_messages, now=now)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
