from flask import Flask, render_template
import os
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from threading import Thread
import json
from flask import request, jsonify
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # จำกัดขนาดไฟล์ที่อัพโหลดไม่เกิน 16MB

# Store the latest photo information
latest_photo = None

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Load credentials from environment variable
credentials_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)

def add_valentine_frame(image_data):
    start_time = datetime.now()
    logging.info("Starting add_valentine_frame")
    # แปลง base64 เป็นรูปภาพ
    image_bytes = base64.b64decode(image_data.split(',')[1])
    image = Image.open(io.BytesIO(image_bytes))
    
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # วาดกรอบสีชมพู
    frame_color = "#FFB6C1"  # สีชมพูอ่อน
    frame_width = 10
    draw.rectangle([(0, 0), (width, height)], outline=frame_color, width=frame_width)
    
    # วาดเมฆสีขาวตามมุมของกรอบ
    cloud_color = "#FFFFFF"
    cloud_positions = [
        (0, 0, 80, 40),  # มุมซ้ายบน
        (width - 100, 0, width, 50),  # มุมขวาบน
        (0, height - 50, 80, height),  # มุมซ้ายล่าง
        (width - 100, height - 50, width, height)  # มุมขวาล่าง
    ]
    for pos in cloud_positions:
        draw.ellipse(pos, fill=cloud_color)
    
    # วาดหัวใจเล็ก ๆ ตามมุมของกรอบ
    heart_color = "#FF69B4"  # สีชมพูสด
    heart_size = 15
    heart_positions = [
        (10, 10),  # มุมซ้ายบน
        (width - 30, 10),  # มุมขวาบน
        (10, height - 30),  # มุมซ้ายล่าง
        (width - 30, height - 30)  # มุมขวาล่าง
    ]
    for x, y in heart_positions:
        draw.polygon([
            (x, y),
            (x + heart_size, y - heart_size),
            (x + 2 * heart_size, y),
            (x + 1.5 * heart_size, y + heart_size),
            (x + 0.5 * heart_size, y + heart_size)
        ], fill=heart_color)

    # แปลงกลับเป็น base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    result = base64.b64encode(buffered.getvalue()).decode('utf-8')
    logging.info("Completed add_valentine_frame in %s", datetime.now() - start_time)
    return result

# Function to upload image to Google Drive
def upload_to_drive(filepath, filename):
    file_metadata = {
        'name': filename,
        'parents': ['1cyo6W45o65fjInm5oLuTf9e4dhvubnr1']
    }
    media = MediaFileUpload(filepath, mimetype='image/jpeg')
    drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

@app.route('/')
def index():
    return render_template('camera.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/dashboard')
def dashboard():
    # Fetch images from local storage or database
    images = [f'/static/uploads/{file}' for file in os.listdir(UPLOAD_FOLDER) if file.endswith('.jpg')]
    return render_template('dashboard.html', images=images)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    start_time = datetime.now()
    logging.info("Starting upload_photo")
    global latest_photo
    
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # เพิ่มกรอบวาเลนไทน์
        image_with_frame = add_valentine_frame(data['image'])
        
        # สร้างชื่อไฟล์ด้วยเวลาปัจจุบัน
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'photo_{timestamp}.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # บันทึกรูปภาพ
        img_data = base64.b64decode(image_with_frame)
        with open(filepath, 'wb') as f:
            f.write(img_data)

        # Run upload in background
        thread = Thread(target=upload_to_drive, args=(filepath, filename))
        thread.start()

        # อัพเดทรูปภาพล่าสุด
        latest_photo = {
            'filepath': f'/static/uploads/{filename}',
            'timestamp': timestamp
        }
        
        result = jsonify({'success': True, 'filepath': latest_photo['filepath']})
        logging.info("Completed upload_photo in %s", datetime.now() - start_time)
        return result
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_latest_photo')
def get_latest_photo():
    return jsonify(latest_photo if latest_photo else {'filepath': None})

if __name__ == '__main__':
    app.run(debug=True)
