import sys
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
import pyodbc

login_bp = Blueprint('login', __name__)


@login_bp.route('/account', methods=['GET', 'POST'])  
def login():
    if request.method == 'POST':
        username_input = request.form['username']
        password_input = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username_input,))
        user = cursor.fetchone()

        # Asumsikan kolom ke-3 (index 3) adalah kolom password
        if user and check_password_hash(user[3], password_input):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home.home'))
        else:
            flash("Username atau password salah", "danger")
            return render_template('loginPage.html')
        
    return render_template('loginPage.html')


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username_input = request.form['username']
        email_input = request.form['email']
        password_input = request.form['password']
        confirm_password_input = request.form.get('confirm_password')

        if password_input != confirm_password_input:
            flash("Password dan konfirmasi tidak cocok", "danger")
            return render_template('loginPage.html')

        hashed_password = generate_password_hash(password_input)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username_input, email_input))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username atau email sudah digunakan", "danger")
                return render_template('loginPage.html')

            cursor.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (username_input, email_input, hashed_password))
            conn.commit()

            flash("Akun berhasil dibuat!", "success")
            return redirect(url_for('login.login'))

        except Exception as e:
            flash(f"Terjadi kesalahan: {str(e)}", "danger")
            return render_template('loginPage.html')
        finally:
            cursor.close()
            conn.close()

    return render_template('loginPage.html')


@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.home'))
