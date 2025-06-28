from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for sessions and flash messages

# Ensure the database is created in the correct location
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'disaster_management.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    reports = db.relationship('Report', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    coordinates = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    solved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def maps_url(self):
        return f"https://www.google.com/maps?q={self.coordinates}"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Create tables
with app.app_context():
    db.create_all()
    # Create admin user if not exists
    admin = User.query.filter_by(username=ADMIN_USERNAME).first()
    if not admin:
        admin = User(username=ADMIN_USERNAME, email="admin@example.com")
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'admin' not in session:
            flash('Admin access required.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapper

def validate_coordinates(coordinates):
    # Clean and validate coordinates
    coords = coordinates.replace(' ', '').strip()
    try:
        lat, long = map(float, coords.split(','))
        if -90 <= lat <= 90 and -180 <= long <= 180:
            return True
        return False
    except:
        return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Admin logged in successfully!')
            return redirect(url_for('admin'))
        else:
            flash('Invalid admin credentials')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    flash('Logged out successfully!')
    return redirect(url_for('home'))

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        coordinates = request.form.get('coordinates')
        description = request.form.get('description')
        
        if name and phone and coordinates and description:
            if not validate_coordinates(coordinates):
                flash('Invalid coordinates format. Please use format: latitude,longitude (e.g., 12.922835,77.50111)')
                return render_template('user.html')
            
            report = Report(
                name=name,
                phone=phone,
                coordinates=coordinates,
                description=description,
                user_id=session['user_id']
            )
            db.session.add(report)
            db.session.commit()
            flash('Report submitted successfully!')
            return redirect(url_for('submission_success'))
        else:
            flash('All fields are required!')
    
    return render_template('user.html')

@app.route('/admin')
@admin_required
def admin():
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    return render_template('admin.html', reports=reports)

@app.route('/admin_action', methods=['POST'])
@admin_required
def admin_action():
    report_id = request.form.get('report_id')
    action = request.form.get('action')
    
    if not report_id or not action:
        flash('Invalid request')
        return redirect(url_for('admin'))
    
    report = Report.query.get_or_404(report_id)
    
    if action == 'solve':
        report.solved = True
        db.session.commit()
        flash('Report marked as solved')
    elif action == 'delete':
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted')
    
    return redirect(url_for('admin'))

@app.route('/submission_success')
@login_required
def submission_success():
    return render_template('submission_success.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables with new schema

        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username=ADMIN_USERNAME).first()
        if not admin:
            admin = User(username=ADMIN_USERNAME, email='admin@example.com')
            admin.set_password(ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True, host='0.0.0.0')