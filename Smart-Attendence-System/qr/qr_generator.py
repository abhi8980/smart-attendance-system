
import qrcode
from datetime import datetime

lecture_id = "CS101_" + datetime.now().strftime("%Y%m%d%H%M")

base_url = "http://localhost:8502/"

full_url = f"{base_url}/?lecture={lecture_id}"

img = qrcode.make(full_url)
img.save("qr/lecture_qr.png")

print("\nQR Generated Successfully!")
print("Lecture Code:", lecture_id)
print("Full URL:", full_url)
