import cv2
import pytesseract
import spacy
import re

# Load custom-trained NER model
nlp = spacy.load("./receipt_ner_model")

def extract_additional_fields(doc, extracted_text):
    extracted_fields = {
        "company": None,
        "address": None,
        "total": None,
        "date": None
    }

    for ent in doc.ents:
        if ent.label_ == "COMPANY" and not extracted_fields["company"]:
            extracted_fields["company"] = ent.text
        elif ent.label_ == "ADDRESS" and not extracted_fields["address"]:
            extracted_fields["address"] = ent.text
        elif ent.label_ == "TOTAL" and not extracted_fields["total"]:
            extracted_fields["total"] = ent.text
        elif ent.label_ == "DATE" and not extracted_fields["date"]:
            extracted_fields["date"] = ent.text

    lines = extracted_text.split('\n')

    # Fallback TOTAL: cari baris berikutnya jika GRAND TOTAL kosong
    for i, line in enumerate(lines):
        if re.search(r'\bgrand\s*total\b', line, re.IGNORECASE):
            total_match = re.search(r'(\d+[.,]?\d*)', line)
            if not total_match and i + 1 < len(lines):
                total_match = re.search(r'(\d+[.,]?\d*)', lines[i+1])
            if total_match:
                # Tambahkan validasi panjang agar tidak salah ambil angka seperti "4132"
                if len(total_match.group(1).replace('.', '').replace(',', '')) >= 2 and len(total_match.group(1)) <= 7:
                    extracted_fields["total"] = total_match.group(1).strip()
                    break

    # Jika belum ditemukan, baru fallback ke "TOTAL", "SUBTOTAL", dsb
    if not extracted_fields["total"]:
        for i, line in enumerate(lines):
            if re.search(r'\b(total|amount|balance|due|jumlah)\b', line, re.IGNORECASE):
                total_match = re.search(r'(\d+[.,]?\d*)', line)
                if not total_match and i + 1 < len(lines):
                    total_match = re.search(r'(\d+[.,]?\d*)', lines[i+1])
                if total_match:
                    extracted_fields["total"] = total_match.group(1).strip()
                    break

    # Fallback DATE 
    if not extracted_fields["date"]:
        for line in lines:
            date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', line)
            if not date_match:
                date_match = re.search(r'\b(January|February|March|...|Desember)\s+\d{1,2},?\s+\d{4}', line, re.IGNORECASE)
            if date_match:
                extracted_fields["date"] = date_match.group(0).strip()
                break

    # Fallback COMPANY
    if not extracted_fields["company"]:
        for line in lines[:4]:
            if re.search(r'(store|mart|pt\.|inc\.|company|supermarket|toko|indomaret|alfamart|tan chay yee)', line, re.IGNORECASE):
                extracted_fields["company"] = line.strip()
                break
        if not extracted_fields["company"]:
            extracted_fields["company"] = lines[0].strip()

    # Fallback ADDRESS
    if not extracted_fields["address"]:
        for i, line in enumerate(lines):
            if re.search(r'(jalan|jl\.|street|road|no\.|blok|kelurahan|kecamatan)', line, re.IGNORECASE):
                address_line = line
                if i + 1 < len(lines):
                    address_line += ' ' + lines[i+1].strip()
                extracted_fields["address"] = address_line.strip()
                break

    return extracted_fields

def preprocess_image(image_path):

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.fastNlMeansDenoising(thresh, h=30)

    return thresh


def process_image(filepath):
   
    image = cv2.imread(filepath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
    n_boxes = len(data['text'])

    # [3] Tampilkan hasil OCR yang confidence-nya tinggi
    for i in range(n_boxes):
        conf = int(data['conf'][i])
        text = data['text'][i].strip()
        if conf > 70 and text:
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1, lineType=cv2.LINE_AA)

   
    extracted_text_lines = []
    current_line_num = -1
    line_words = []

    for i in range(n_boxes):
        conf = int(data['conf'][i])
        text = data['text'][i].strip()
        line_num = data['line_num'][i]
        if conf > 70 and text:
            if line_num != current_line_num:
                if line_words:
                    extracted_text_lines.append(' '.join(line_words))
                line_words = [text]
                current_line_num = line_num
            else:
                line_words.append(text)
    if line_words:
        extracted_text_lines.append(' '.join(line_words))

    extracted_text = '\n'.join(extracted_text_lines)

  
    clean_text = extracted_text.lower()
    clean_text = re.sub(r'[^\x00-\x7F]+', ' ', clean_text)
    clean_text = re.sub(r'[\|_]', '', clean_text)

    # [6] Jalankan NER
    doc = nlp(clean_text)
    extracted_fields = extract_additional_fields(doc, clean_text)

    # [7] Print debug
    print("OCR TEXT:\n", extracted_text)
    print("NER ENTITIES:\n", [(ent.text, ent.label_) for ent in doc.ents])
    print("EXTRACTED FIELDS:\n", extracted_fields)

    return image, extracted_text, extracted_fields
