from flask import Blueprint, render_template, session, flash, redirect, url_for
from db import get_db_connection
import pyodbc

result_bp = Blueprint('result', __name__)

@result_bp.route('/Extraction-result')
def result():
    user_id = session.get('user_id')
    if not user_id:
        flash("Silakan login untuk melihat hasil ekstraksi.", "danger")
        return redirect('/account')

    conn = None
    cursor = None
    results = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ExtractionResults WHERE user_id = ?", (user_id,))
        results = cursor.fetchall()

    except Exception as e:
        flash(f"Terjadi kesalahan saat mengambil data: {str(e)}", "danger")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template('trackingPage.html', results=results)
