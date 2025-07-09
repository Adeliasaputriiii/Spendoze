from flask import Blueprint, request, redirect, session, render_template, flash
from db import get_db_connection
import pyodbc

save_bp = Blueprint('save', __name__)

@save_bp.route('/save-extraction', methods=['POST'])
def save_extraction():
    extracted_fields = request.form.to_dict()
    image_path = request.form.get('image_path')
    user_id = session.get('user_id')

    print("DEBUG - Save Extraction")
    print("User ID:", user_id)
    print("Image Path:", image_path)
    print("Extracted Fields:", extracted_fields)

    if not user_id:
        flash("Silakan login terlebih dahulu.", "danger")
        return redirect('/account')

    # Validasi field penting tidak kosong atau bernilai 'None'
    if not all([
        extracted_fields.get('company'),
        extracted_fields.get('date'),
        extracted_fields.get('total') not in [None, '', 'None']
    ]):
        flash("Data tidak lengkap. Pastikan semua field terisi.", "danger")
        return render_template(
            'uploadPage.html',
            extracted_fields=extracted_fields,
            uploaded_image=image_path,
            save_success=False
        )

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ExtractionResults (user_id, company, address, total, date, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            extracted_fields.get('company'),
            extracted_fields.get('address'),
            extracted_fields.get('total'),
            extracted_fields.get('date'),
            image_path
        ))
        conn.commit()
        flash("Data berhasil disimpan ke database.", "success")

    except Exception as e:
        flash(f"Terjadi kesalahan saat menyimpan: {str(e)}", "danger")
        print("ERROR saat menyimpan:", str(e))

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template(
        'uploadPage.html',
        extracted_fields=extracted_fields,
        uploaded_image=image_path,
        save_success=True
    )
