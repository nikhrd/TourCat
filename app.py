from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    return render_template('event_detail.html', event_id=event_id)

# Login routes
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/customer')
def login_customer():
    return render_template('login_customer.html')

@app.route('/login/manager')
def login_manager():
    return render_template('login_manager.html')

@app.route('/manager/dashboard')
def manager_dashboard():
    return render_template('event_manager_dashboard.html')

@app.route('/book/<int:event_id>')
def book_event(event_id):
    return render_template('book_event.html', event_id=event_id)

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/manager/events')
def manager_uploaded_events():
    return render_template('uploaded_events.html')

if __name__ == '__main__':
    app.run(debug=True)
