import requests
import pytesseract
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import cv2
import numpy as np
import datetime
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# Initialize pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to retrieve CAPTCHA image using Selenium
def get_captcha_image(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    time.sleep(5)
    
    def get_captcha_image(driver):
        try:
            # Don't call driver.get() here since it's already done in main.py
            captcha_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "captcha_image"))
            )
            
            # Get the image data
            captcha_image = Image.open(io.BytesIO(captcha_element.screenshot_as_png))
            return captcha_image
            
        except Exception as e:
            print(f"Error getting CAPTCHA: {str(e)}")
            return None
    
    captcha_img_element = driver.find_element(By.ID, 'captcha_image')
    captcha_url = captcha_img_element.get_attribute('src')
    captcha_image_response = requests.get(captcha_url)
    
    image = Image.open(io.BytesIO(captcha_image_response.content))
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captcha_{timestamp}.png"
    filepath = os.path.join(os.getcwd(), filename)
    image.save(filepath)
    print(f"[INFO] CAPTCHA image saved to: {filepath}")
    
    driver.quit()
    
    return image

# Function to preprocess the image for better OCR accuracy
def preprocess_image(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Apply thresholding to improve contrast
    _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return thresh_image

# Function to perform OCR on the CAPTCHA image
def ocr_captcha(image):
    # Preprocess the image
    processed_image = preprocess_image(image)
    
    # Perform OCR to extract text
    captcha_text = pytesseract.image_to_string(processed_image, config='--psm 6')
    
    # Clean up the OCR result (remove unwanted characters or newlines)
    captcha_text = captcha_text.strip()
    
    return captcha_text

# Main function to perform the task
def main():
    # URL with CNR number
    url = 'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index&app_token=766b23635c4303220cbb8e8b04568d6fccc37a66e55486952fd64d9c0a1b5e25'
    
    # Get CAPTCHA image
    captcha_image = get_captcha_image(url)
    
    # Use OCR to detect the CAPTCHA text
    captcha_text = ocr_captcha(captcha_image)
    
    print(f"Detected CAPTCHA Text: {captcha_text}")
    
    # Further steps would include submitting the form using the detected CAPTCHA text,
    # scraping the data, and saving it to a JSON file. 
    
    # Example JSON output format
    output_data = {
        "CNR1": "GJAH240000792025",
        "CNR2": "GJAH240026012021",
        "CNR3": "GJAH240007312023",
        "Detected_Captcha": captcha_text
    }
    
    # Saving the output to a JSON file
    import json
    with open("Output.json", "w") as outfile:
        json.dump(output_data, outfile, indent=4)

# Run the main function
if __name__ == "__main__":
    main()
