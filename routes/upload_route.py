# routes/upload_route.py
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from utils.ocr_utils import process_image

upload_bp = Blueprint('upload', __name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/extraction-to-text', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Proses gambar & ekstrak field menggunakan OCR + NER
            image, extracted_text, extracted_fields = process_image(filepath)
            relative_path = os.path.relpath(filepath, 'static')

            return render_template('uploadPage.html',
                       uploaded_image=relative_path.replace("\\", "/"),
                       extracted_fields=extracted_fields,
                       image_path=relative_path.replace("\\", "/"))

    return render_template('uploadPage.html')
