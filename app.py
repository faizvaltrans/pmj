from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATA_FILE = 'members.csv'
PAYMENTS_FILE = 'payments.csv'

# Load members from CSV
def load_members():
    members = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                members[row['id']] = row
    return members

# Load payments from CSV
def load_payments():
    payments = []
    if os.path.exists(PAYMENTS_FILE):
        with open(PAYMENTS_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                payments.append(row)
    return payments

# Save members to CSV
def save_members(members):
    with open(DATA_FILE, 'w', newline='') as csvfile:
        fieldnames = ['id', 'name', 'phone', 'emirate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for m in members.values():
            writer.writerow(m)

# Save payments to CSV
def save_payments(payments):
    with open(PAYMENTS_FILE, 'w', newline='') as csvfile:
        fieldnames = ['id', 'member_id', 'year_month', 'amount', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for p in payments:
            writer.writerow(p)

# Dummy user login data
users = {
    "superadmin": {"password": "admin123", "role": "superadmin", "emirate": None},
    "dubaiadmin": {"password": "dubai123", "role": "admin", "emirate": "Dubai"},
    "sharjahadmin": {"password": "sharjah123", "role": "admin", "emirate": "Sharjah"}
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            session['emirate'] = user['emirate']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    members = load_members()
    payments = load_payments()
    # Filter members by emirate for admin role
    if session['role'] == 'admin':
        members = {k:v for k,v in members.items() if v['emirate'] == session['emirate']}
    return render_template('dashboard.html', members=members, payments=payments)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if 'username' not in session or session['role'] not in ['admin', 'superadmin']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        members = load_members()
        new_id = str(len(members)+1)
        members[new_id] = {
            'id': new_id,
            'name': request.form['name'],
            'phone': request.form['phone'],
            'emirate': request.form['emirate']
        }
        save_members(members)
        flash('Member added successfully')
        return redirect(url_for('dashboard'))
    return render_template('add_member.html')

@app.route('/add_payment/<member_id>', methods=['GET', 'POST'])
def add_payment(member_id):
    if 'username' not in session or session['role'] not in ['admin', 'superadmin']:
        return redirect(url_for('login'))
    members = load_members()
    if member_id not in members:
        flash('Member not found')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        payments = load_payments()
        new_payment = {
            'id': str(len(payments)+1),
            'member_id': member_id,
            'year_month': request.form['year_month'],
            'amount': request.form['amount'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        payments.append(new_payment)
        save_payments(payments)
        flash('Payment added successfully')
        return redirect(url_for('dashboard'))
    return render_template('add_payment.html', member=members[member_id])

if __name__ == '__main__':
    app.run(debug=True)