import cv2
import numpy as np
import pyperclip
from PIL import ImageGrab
import io
import pyotp

try:
    # Read the image from the clipboard
    image = ImageGrab.grabclipboard()
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes = image_bytes.getvalue()

    # Convert to a format readable by cv2
    image_np = np.frombuffer(image_bytes, dtype=np.uint8)
    image_cv = cv2.imdecode(image_np, flags=cv2.IMREAD_COLOR)

    # Decode the QR code
    detector = cv2.QRCodeDetector()
    data, vertices_array, binary_qrcode = detector.detectAndDecode(image_cv)

    start = data.find('secret=') + len('secret=')
    end = data.find('&', start)
    secret = data[start:end]

    # Generate a TOTP code
    totp = pyotp.TOTP(secret)
    totp_code = totp.now()

    print(f"Secret key = {secret} \n TOTP Code = {totp_code}")

except Exception as e:
    print(f"**The image didnt found in clipboard or unreadable**\nError occurred: {str(e)}")
