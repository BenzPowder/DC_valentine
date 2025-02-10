import qrcode

# สร้าง QR Code สำหรับติดหน้าประตู
# URL ที่จะใช้เมื่อแสกน QR Code
url = "http://localhost:5000/camera"

# สร้าง QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# สร้างรูปภาพ QR Code
qr_image = qr.make_image(fill_color="black", back_color="white")

# บันทึกไฟล์
qr_image.save("static/entrance_qr.png")
