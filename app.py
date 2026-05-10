import os
import datetime
import threading
from functools import wraps

import joblib
import pandas as pd
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from database.mongo import get_collection, get_database

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-now')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
app.config['TEMPLATES_AUTO_RELOAD'] = True

MODEL_PATH = os.path.join(app.root_path, 'models', 'model.pkl')
FEATURE_COLUMNS = [
    'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
    'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
    'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount'
]

user_collection = get_collection('users')
transaction_collection = get_collection('transactions')
model = None


def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"Loaded model from {MODEL_PATH}")
    else:
        model = None
        print('Model file not found. Please train the model first.')


def serialize_object_id(document):
    document['_id'] = str(document['_id'])
    return document


def create_user(name, email, password, role='user'):
    password_hash = generate_password_hash(password)
    user_collection.insert_one({
        'name': name,
        'email': email.lower(),
        'password': password_hash,
        'role': role,
        'created_at': datetime.datetime.utcnow()
    })


def get_user_by_email(email):
    return user_collection.find_one({'email': email.lower()})


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Administrator access required.', 'danger')
            return redirect(url_for('dashboard'))
        return view(**kwargs)
    return wrapped_view


def normalize_transaction(payload):
    row = {}
    for column in FEATURE_COLUMNS:
        value = payload.get(column, 0)
        try:
            row[column] = float(value)
        except (TypeError, ValueError):
            row[column] = 0.0
    return row


def save_prediction_record(record):
    transaction_collection.insert_one(record)


def process_transactions_in_background(transactions, user_id, email):
    for transaction in transactions:
        try:
            normalized = normalize_transaction(transaction)
            df = pd.DataFrame([normalized], columns=FEATURE_COLUMNS)
            prediction = int(model.predict(df)[0])
            probability = float(model.predict_proba(df)[0][1])
            document = {
                'user_id': user_id,
                'email': email,
                'features': normalized,
                'prediction': prediction,
                'probability': probability,
                'created_at': datetime.datetime.utcnow(),
                'source': 'batch'
            }
            save_prediction_record(document)
        except Exception:
            continue


def ensure_admin_user():
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if admin_email and admin_password:
        existing = user_collection.find_one({'email': admin_email.lower(), 'role': 'admin'})
        if not existing:
            create_user('Admin', admin_email, admin_password, role='admin')
            print('Admin user created from environment variables.')


@app.route('/')
def home():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('index.html', page_name='home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['name'] = user['name']
            session['role'] = user.get('role', 'user')
            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', page_name='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not name or not email or not password:
            flash('Please complete all required fields.', 'warning')
            return render_template('register.html', page_name='register')

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('register.html', page_name='register')

        if get_user_by_email(email):
            flash('Email is already registered.', 'warning')
            return render_template('register.html', page_name='register')

        create_user(name, email, password)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', page_name='register')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', page_name='dashboard')


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html', page_name='admin')


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if model is None:
        return jsonify({'success': False, 'error': 'Model is not loaded.'}), 500

    payload = request.get_json(silent=True) or {}
    data = payload.get('features') if isinstance(payload.get('features'), dict) else payload

    normalized = normalize_transaction(data)
    df = pd.DataFrame([normalized], columns=FEATURE_COLUMNS)
    prediction = int(model.predict(df)[0])
    probability = float(model.predict_proba(df)[0][1])
    result = {
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'features': normalized,
        'prediction': prediction,
        'probability': probability,
        'created_at': datetime.datetime.utcnow(),
        'source': 'live'
    }
    threading.Thread(target=save_prediction_record, args=(result,), daemon=True).start()

    return jsonify({
        'success': True,
        'prediction': 'fraud' if prediction == 1 else 'safe',
        'probability': round(probability * 100, 2),
        'record': result
    })


@app.route('/process_transactions', methods=['POST'])
@login_required
def process_transactions():
    payload = request.get_json(silent=True) or {}
    transactions = payload.get('transactions')

    if not isinstance(transactions, list) or len(transactions) == 0:
        return jsonify({'success': False, 'error': 'Provide a list of transactions.'}), 400

    threading.Thread(
        target=process_transactions_in_background,
        args=(transactions, session.get('user_id'), session.get('email')),
        daemon=True
    ).start()

    return jsonify({'success': True, 'message': 'Background processing started.'})


@app.route('/api/analytics')
@login_required
def api_analytics():
    is_admin = session.get('role') == 'admin'
    match = {} if is_admin else {'user_id': session.get('user_id')}

    total = transaction_collection.count_documents(match)
    fraud = transaction_collection.count_documents({**match, 'prediction': 1})
    safe = total - fraud
    average_probability = list(transaction_collection.aggregate([
        {'$match': match},
        {'$group': {'_id': None, 'avgProbability': {'$avg': '$probability'}}}
    ]))
    average_probability = round(average_probability[0]['avgProbability'] * 100, 2) if average_probability else 0.0

    recent_transactions = []
    for doc in transaction_collection.find(match).sort('created_at', -1).limit(6):
        doc = serialize_object_id(doc)
        doc['created_at'] = doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        recent_transactions.append(doc)

    return jsonify({
        'total_transactions': total,
        'fraud_count': fraud,
        'safe_count': safe,
        'average_probability': average_probability,
        'recent_transactions': recent_transactions
    })


@app.route('/api/transactions')
@login_required
def api_transactions():
    is_admin = session.get('role') == 'admin'
    query = {} if is_admin else {'user_id': session.get('user_id')}
    search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip().lower()

    if status_filter == 'fraud':
        query['prediction'] = 1
    elif status_filter == 'safe':
        query['prediction'] = 0

    if search:
        query['$or'] = [
            {'email': {'$regex': search, '$options': 'i'}},
            {'user_id': {'$regex': search, '$options': 'i'}}
        ]

    docs = list(transaction_collection.find(query).sort('created_at', -1).limit(100))
    for doc in docs:
        doc = serialize_object_id(doc)
        doc['created_at'] = doc['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        doc['status'] = 'Fraud' if doc.get('prediction') == 1 else 'Safe'
    return jsonify({'transactions': docs})


@app.route('/api/users')
@admin_required
def api_users():
    docs = list(user_collection.find().sort('created_at', -1).limit(100))
    users = []
    for doc in docs:
        users.append({
            'id': str(doc['_id']),
            'name': doc['name'],
            'email': doc['email'],
            'role': doc.get('role', 'user'),
            'created_at': doc['created_at'].strftime('%Y-%m-%d')
        })
    return jsonify({'users': users})


@app.route('/api/status')
@login_required
def api_status():
    database_status = get_database().client is not None
    return jsonify({
        'model_loaded': model is not None,
        'database_connected': database_status,
        'user': session.get('email'),
        'role': session.get('role')
    })


if __name__ == '__main__':
    ensure_admin_user()
    load_model()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
