import qrcode
from datetime import datetime

lecture_id = "CS101_" + datetime.now().strftime("%Y%m%d%H%M")

img = qrcode.make(lecture_id)
img.save("lecture_qr.png")

print("QR Generated:", lecture_id)