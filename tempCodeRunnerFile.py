from ocr_captcha_testing import get_captcha_image, ocr_captcha
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# URL
url = 'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index&app_token=766b23635c4303220cbb8e8b04568d6fccc37a66e55486952fd64d9c0a1b5e25'

# Setup single browser session
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get(url)

# Step 1: Extract CAPTCHA image using existing session
captcha_image = get_captcha_image(driver)

# Step 2: OCR on CAPTCHA
captcha_text = ocr_captcha(captcha_image)
print(f"[INFO] Extracted CAPTCHA Text: {captcha_text}")

# Step 3: Fill CNR and CAPTCHA fields
cnr_number = "GJAH240000792025"
driver.find_element(By.ID, "cnrno").send_keys(cnr_number)
driver.find_element(By.ID, "captcha").send_keys(captcha_text)
driver.find_element(By.ID, "searchbtn").click()

# Step 4: Wait and scrape
time.sleep(5)

try:
    result_table = driver.find_element(By.ID, "case_status_table")
    print("[SUCCESS] Case Information:")
    print(result_table.text)
except Exception as e:
    print("[ERROR] Failed to retrieve case info. Possibly CAPTCHA failed or page changed.")
    print(f"Details: {e}")

driver.quit()
