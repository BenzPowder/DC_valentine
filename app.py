from flask import Flask, render_template, request, jsonify
import os
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # จำกัดขนาดไฟล์ที่อัพโหลดไม่เกิน 16MB

# Store the latest media information
latest_photo = None
latest_video = None

def add_valentine_frame(image_data):
    # แปลง base64 เป็นรูปภาพ
    image_bytes = base64.b64decode(image_data.split(',')[1])
    img = Image.open(io.BytesIO(image_bytes))
    
    # ปรับขนาดรูปภาพให้เป็นสี่เหลี่ยมจัตุรัส
    size = max(img.size)
    new_img = Image.new('RGB', (size, size), 'white')
    offset = ((size - img.size[0]) // 2, (size - img.size[1]) // 2)
    new_img.paste(img, offset)
    
    # สร้างกรอบหัวใจ
    draw = ImageDraw.Draw(new_img)
    
    # วาดกรอบสีชมพู
    border_color = "#FF69B4"  # สีชมพู
    border_width = 20
    draw.rectangle([0, 0, size-1, size-1], outline=border_color, width=border_width)
    
    # วาดหัวใจที่มุม
    heart_size = 50
    heart_color = "#FF1493"  # สีชมพูเข้ม
    
    # วาดหัวใจที่มุมทั้ง 4 มุม
    hearts = [(0, 0), (size-heart_size, 0), (0, size-heart_size), (size-heart_size, size-heart_size)]
    for x, y in hearts:
        draw.polygon([
            (x + heart_size//2, y + heart_size//4),
            (x + heart_size//4, y),
            (x, y + heart_size//4),
            (x + heart_size//2, y + heart_size),
            (x + heart_size, y + heart_size//4),
            (x + heart_size*3//4, y)
        ], fill=heart_color)
    
    # แปลงรูปภาพกลับเป็น base64
    buffered = io.BytesIO()
    new_img.save(buffered, format="JPEG", quality=85)  # ลดคุณภาพลงเล็กน้อยเพื่อประหยัดพื้นที่
    return f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode()}"

@app.route('/')
def index():
    # Redirect to camera page
    return render_template('camera.html')

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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
        img_data = base64.b64decode(image_with_frame.split(',')[1])
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        # อัพเดทรูปภาพล่าสุด
        latest_photo = {
            'filepath': f'/static/uploads/{filename}',
            'timestamp': timestamp
        }
        
        return jsonify({'success': True, 'filepath': latest_photo['filepath']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    global latest_video
    
    try:
        data = request.json
        if not data or 'video' not in data:
            return jsonify({'error': 'No video data provided'}), 400
        
        # สร้างชื่อไฟล์ด้วยเวลาปัจจุบัน
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'video_{timestamp}.webm'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # บันทึกวิดีโอ
        video_data = base64.b64decode(data['video'].split(',')[1])
        with open(filepath, 'wb') as f:
            f.write(video_data)
        
        # อัพเดทวิดีโอล่าสุด
        latest_video = {
            'filepath': f'/static/uploads/{filename}',
            'timestamp': timestamp
        }
        
        return jsonify({'success': True, 'filepath': latest_video['filepath']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_latest_photo')
def get_latest_photo():
    return jsonify(latest_photo if latest_photo else {'filepath': None})

@app.route('/get_latest_video')
def get_latest_video():
    return jsonify(latest_video if latest_video else {'filepath': None})

if __name__ == '__main__':
    # ใช้ port จาก environment variable ถ้ามี (สำหรับ production)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
