import json
from ocr_captcha_testing import ocr_captcha
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
import io
import os

def get_captcha_from_page(driver):
    try:
        captcha_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "captcha_image"))
        )
        captcha_image = Image.open(io.BytesIO(captcha_element.screenshot_as_png))
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        os.makedirs("captcha_images", exist_ok=True)
        original_path = f"captcha_images/original_{timestamp}.png"
        captcha_image.save(original_path)
        print(f"[INFO] CAPTCHA saved to: {original_path}")
        return captcha_image
    except Exception as e:
        print(f"[ERROR] Capturing CAPTCHA: {e}")
        return None

def fetch_case_details_by_cnr(cnr_number: str):
    url = 'https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index&app_token=7b7f35925d60c0fd5f0846a39f4f546c29ffebb8ecb63bef33fcf04679cbdf64'
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(options=options)

    data_output = {}

    try:
        driver.get(url)
        print("[INFO] Page loaded. Waiting for CAPTCHA...")
        time.sleep(3)

        captcha_image = get_captcha_from_page(driver)
        if not captcha_image:
            print("[ERROR] CAPTCHA image not available.")
            return None

        captcha_text = ocr_captcha(captcha_image)
        captcha_text = ''.join(c for c in captcha_text if c.isalnum()).lower()
        print(f"[INFO] Extracted CAPTCHA Text: {captcha_text}")

        wait = WebDriverWait(driver, 15)
        cnr_input = wait.until(EC.presence_of_element_located((By.ID, "cino")))
        cnr_input.clear()
        cnr_input.send_keys(cnr_number)
        print(f"[INFO] CNR input set: {cnr_number}")

        captcha_input = wait.until(EC.presence_of_element_located((By.ID, "fcaptcha_code")))
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)

        wait.until(EC.element_to_be_clickable((By.ID, "searchbtn"))).click()
        print("[INFO] Form submitted. Waiting for result...")

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "case_details_table"))
        )
        time.sleep(2)

        try:
            data_output["Case Details"] = {
                "Case Type": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Case Type')]/following-sibling::td").text.strip(),
                "Filing Number": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Filing Number')]/following-sibling::td").text.strip(),
                "Filing Date": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Filing Date')]/following-sibling::td").text.strip(),
                "Registration Number": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Registration Number')]/following-sibling::td").text.strip(),
                "Registration Date": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Registration Date')]/following-sibling::td").text.strip(),
                "CNR Number": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'CNR Number')]/following-sibling::td/span").text.strip(),
            }
        except Exception as e:
            print(f"[ERROR] Extracting case details: {e}")

        try:
            status_table = driver.find_element(By.XPATH, "//table[contains(@class, 'case_status_table')]")
            rows = status_table.find_elements(By.TAG_NAME, "tr")
            data_output["Case Status"] = {
                "First Hearing Date": rows[0].find_elements(By.TAG_NAME, "td")[1].text.strip(),
                "Next Hearing Date": rows[1].find_elements(By.TAG_NAME, "td")[1].text.strip(),
                "Case Stage": rows[2].find_elements(By.TAG_NAME, "td")[1].text.strip(),
                "Court Number and Judge": rows[3].find_elements(By.TAG_NAME, "td")[1].text.strip()
            }
        except Exception as e:
            print(f"[ERROR] Extracting case status: {e}")

        try:
            data_output["Petitioner and Advocate"] = driver.find_element(
                By.XPATH, "//table[contains(@class, 'Petitioner_Advocate_table')]//td"
            ).text.strip()
        except Exception as e:
            print(f"[ERROR] Petitioner/Advocate: {e}")

        try:
            data_output["Respondent and Advocate"] = driver.find_element(
                By.XPATH, "//table[contains(@class, 'Respondent_Advocate_table')]//td"
            ).text.strip()
        except Exception as e:
            print(f"[ERROR] Respondent/Advocate: {e}")

        try:
            acts_table = driver.find_element(By.XPATH, "//table[contains(@class, 'acts_table')]")
            rows = acts_table.find_elements(By.TAG_NAME, "tr")
            data_output["Acts"] = {
                "Under Act(s)": rows[1].find_elements(By.TAG_NAME, "td")[0].text.strip(),
                "Under Section(s)": rows[1].find_elements(By.TAG_NAME, "td")[1].text.strip()
            }
        except Exception as e:
            print(f"[ERROR] Acts: {e}")

        try:
            history_table = driver.find_element(By.XPATH, "//table[contains(@class, 'history_table')]")
            history_rows = history_table.find_elements(By.TAG_NAME, "tr")
            history = []
            for row in history_rows[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 4:
                    history.append({
                        "Judge": cols[0].text.strip(),
                        "Business on Date": cols[1].text.strip(),
                        "Hearing Date": cols[2].text.strip(),
                        "Purpose of Hearing": cols[3].text.strip()
                    })
            data_output["Case History"] = history
        except Exception as e:
            print(f"[ERROR] Case History: {e}")

    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        driver.save_screenshot("fatal_error.png")

    finally:
        driver.quit()
    
    if data_output:
        os.makedirs("case_outputs", exist_ok=True)
        with open(f"case_outputs/{cnr_number}.json", "w", encoding="utf-8") as f:
            json.dump(data_output, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Case data saved to case_outputs/{cnr_number}.json")


    return data_output
