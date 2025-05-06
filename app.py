from flask import Flask, render_template, request, redirect, url_for, session
from extensions import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from models import User, Event, Booking
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'niuha'

# Database setup
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tourcat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db.init_app(app)
login_manager.init_app(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Redirect unauthorized users to login
login_manager.login_view = 'login'

# Create tables
with app.app_context():
    db.create_all()
users = {
    'customer': {'email': 'cust@example.com', 'password': 'pass123'},
    'manager': {'email': 'mgr@example.com', 'password': 'admin123'}
}

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/')
def home():
    user = session.get('user')
    return render_template('home.html', user=user)
@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    return render_template('event_detail.html', event_id=event_id)


# ---------------- LOGIN / LOGOUT ----------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        user = User.query.filter_by(username=username, password=password, role=role).first()
        if user:
            login_user(user)
            if user.role == 'customer':
                return redirect(url_for('customer_dashboard'))
            else:
                return redirect(url_for('manager_dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/login/customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == users['customer']['email'] and password == users['customer']['password']:
            session['user'] = {'type': 'customer', 'email': email}
            return redirect(url_for('home'))
        return "Invalid credentials for customer"
    return render_template('login_customer.html')

@app.route('/login/manager', methods=['GET', 'POST'])
def login_manager():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == users['manager']['email'] and password == users['manager']['password']:
            session['user'] = {'type': 'manager', 'email': email}
            return redirect(url_for('manager_dashboard'))
        return "Invalid credentials for manager"
    return render_template('login_manager.html')


# ---------------- DASHBOARDS ----------------

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        return "Access Denied"
    events = Event.query.all()
    return render_template('customer_dashboard.html', events=events)

@app.route('/manager/dashboard', methods=['GET', 'POST'])
@login_required
def manager_dashboard():
    if current_user.role != 'manager':
        return "Access Denied"
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        date = request.form['date']
        
        event = Event(title=title, description=description, location=location, date=date, manager_id=current_user.id)
        db.session.add(event)
        db.session.commit()
    
    events = Event.query.filter_by(manager_id=current_user.id).all()
    return render_template('event_manager_dashboard.html', events=events)


# ---------------- BOOKINGS ----------------

@app.route('/book/<int:event_id>')
@login_required
def book_event(event_id):
    if current_user.role != 'customer':
        return "Only customers can book."
    
    booking = Booking(event_id=event_id, customer_id=current_user.id)
    db.session.add(booking)
    db.session.commit()
    
    return redirect(url_for('customer_dashboard'))


# ---------------- MISC ----------------

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/manager/events')
def manager_uploaded_events():
    return render_template('uploaded_events.html')


if __name__ == '__main__':
    app.run(debug=True)
