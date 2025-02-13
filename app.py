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
    # แปลง base64 เป็นรูปภาพ
    image_bytes = base64.b64decode(image_data.split(',')[1])
    image = Image.open(io.BytesIO(image_bytes))
    
    # เพิ่มกรอบวาเลนไทน์
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    # วาดกรอบสีแดง
    draw.rectangle([(0, 0), (width, height)], outline="red", width=5)
    
    # วาดเมฆ
    cloud_color = "#D3D3D3"  # สีเทาอ่อน
    draw.ellipse([(width * 0.1, height * 0.1), (width * 0.3, height * 0.2)], fill=cloud_color)
    draw.ellipse([(width * 0.2, height * 0.15), (width * 0.4, height * 0.25)], fill=cloud_color)
    
    # วาดหัวใจ
    heart_color = "#FF69B4"  # สีชมพู
    heart_size = 20
    for x, y in [(width * 0.7, height * 0.7), (width * 0.8, height * 0.8)]:
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
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

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
        
        return jsonify({'success': True, 'filepath': latest_photo['filepath']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_latest_photo')
def get_latest_photo():
    return jsonify(latest_photo if latest_photo else {'filepath': None})

if __name__ == '__main__':
    app.run(debug=True)
