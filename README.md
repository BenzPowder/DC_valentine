# Valentine's Day Concert Photo Booth

ระบบถ่ายรูปสำหรับงานคอนเสิร์ตวันวาเลนไทน์ ที่ให้ผู้เข้าร่วมงานสแกน QR Code เพื่อถ่ายรูป และแสดงผลบน Dashboard พร้อมกรอบรูปธีมวันวาเลนไทน์

## การติดตั้งสำหรับพัฒนา

1. ติดตั้ง Python 3.12 หรือสูงกว่า
2. ติดตั้ง dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. สร้าง QR Code สำหรับติดหน้างาน:
   ```bash
   python generate_qr.py
   ```
4. รันแอพพลิเคชัน:
   ```bash
   python app.py
   ```

## การ Deploy บน Render.com

1. สร้าง Git repository และ push โค้ดขึ้นไป
2. ไปที่ [Render.com](https://render.com) และ sign in
3. กด "New +" และเลือก "Web Service"
4. เชื่อมต่อกับ Git repository ของคุณ
5. ตั้งค่าดังนี้:
   - Name: valentine-photo-booth (หรือชื่อที่ต้องการ)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. กด "Create Web Service"

## การใช้งาน

1. พิมพ์ QR Code จากไฟล์ `static/entrance_qr.png` และติดไว้ที่หน้างาน
2. ให้ผู้เข้าร่วมงานสแกน QR Code ด้วยมือถือ
3. ผู้เข้าร่วมงานถ่ายรูปและกดส่ง
4. รูปจะปรากฏบน Dashboard ที่เปิดไว้ พร้อมกรอบรูปธีมวันวาเลนไทน์

## หมายเหตุ

- ต้องแน่ใจว่าโฟลเดอร์ `static/uploads` มีสิทธิ์ในการเขียนไฟล์
- ในโหมด production ควรใช้ cloud storage แทนการเก็บไฟล์ในเครื่อง
- สามารถปรับแต่งธีมและการแสดงผลได้ที่ไฟล์ `templates/dashboard.html`
