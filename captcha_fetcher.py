import requests
from PIL import Image
from io import BytesIO
import pytesseract
from PIL import ImageEnhance, ImageFilter
import cv2
import numpy as np

captcha_url = "<DUMMY_LINK_FOR_YOUR_CAPTCHA_REPLACE_THIS>"
referer_url = "<DUMMY_REFERER_URL_REPLACE_THIS>"


# Set headers
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": referer_url,
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin"
}

# Creates a session
session = requests.Session()
1
# Get initial session cookie
response = session.get(referer_url, headers=headers)

# Fetch CAPTCHA image
captcha_response = session.get(captcha_url, headers=headers)

if captcha_response.status_code == 200:
    image = Image.open(BytesIO(captcha_response.content))
    
    # Save original CAPTCHA image
    image.save("original_captcha.png")
    
    # Preprocess image
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Remove noise
    kernel = np.ones((2, 2), np.uint8)
    image = cv2.erode(image, kernel, iterations=2)
    image = cv2.dilate(image, kernel, iterations=2)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image = clahe.apply(image)
    
    # Apply bilateral filter
    image = cv2.bilateralFilter(image, 9, 75, 75)
    
    # Save processed CAPTCHA image
    cv2.imwrite("processed_captcha.png", image)
    
    # Configure Tesseract-OCR
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    
    captcha_text = pytesseract.image_to_string(image, config=custom_config)
    print("Extracted CAPTCHA text:", captcha_text.strip())
else:
    print("Failed to fetch CAPTCHA image. Status code:", captcha_response.status_code)