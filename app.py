from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timecapsule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------
# Database Model
# -------------------------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    content = db.Column(db.Text)
    open_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_open(self):
        return datetime.utcnow() >= self.open_date

# -------------------------
# Routes
# -------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        username = request.form['username']
        content = request.form['content']
        open_date_str = request.form['open_date']  # e.g. 2025-12-31
        open_date = datetime.strptime(open_date_str, '%Y-%m-%d')
        
        message = Message(username=username, content=content, open_date=open_date)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('messages'))
    return render_template('submit.html')

@app.route('/messages')
def messages():
    # Only show messages whose open_date has passed
    open_messages = Message.query.all()
    return render_template('messages.html', messages=open_messages, now=datetime.utcnow())

# -------------------------
# Run the app
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # create DB tables
    app.run(debug=True)
