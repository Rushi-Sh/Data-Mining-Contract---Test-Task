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
        return captcha_image, original_path
    except Exception as e:
        print(f"[ERROR] Capturing CAPTCHA: {e}")
        return None, None

def select_dropdowns(driver):
    try:
        print("[INFO] Selecting state, district, and court complex...")
        Select(driver.find_element(By.ID, "stateCode")).select_by_visible_text("Gujarat")
        time.sleep(2)
        Select(driver.find_element(By.ID, "distCode")).select_by_visible_text("Ahmedabad")
        time.sleep(2)
        Select(driver.find_element(By.ID, "courtCode")).select_by_visible_text("Addl. Court Dholka")
        time.sleep(1)
        print("[INFO] Dropdowns set successfully.")
    except Exception as e:
        print(f"[ERROR] While selecting dropdowns: {e}")
        driver.save_screenshot("error_state.png")
        raise

# Setup
url = 'https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index&app_token=7b7f35925d60c0fd5f0846a39f4f546c29ffebb8ecb63bef33fcf04679cbdf64'
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Uncomment for headless
driver = webdriver.Chrome(options=options)

data_output = {}

try:
    driver.get(url)
    print("[INFO] Page loaded. Waiting for CAPTCHA...")
    time.sleep(3)

    captcha_image, image_path = get_captcha_from_page(driver)

    if captcha_image:
        captcha_text = ocr_captcha(captcha_image)
        captcha_text = ''.join(c for c in captcha_text if c.isalnum()).lower()
        print(f"[INFO] Extracted CAPTCHA Text: {captcha_text}")

        wait = WebDriverWait(driver, 15)

        search_mode = "cnr"
        if search_mode == "cnr":
            cnr_input = wait.until(EC.presence_of_element_located((By.ID, "cino")))
            cnr_value = "GJAH240000792025"
            cnr_input.clear()
            cnr_input.send_keys(cnr_value)
            print("[INFO] CNR input set.")
        else:
            select_dropdowns(driver)
            driver.find_element(By.ID, "rad_party").click()
            time.sleep(1)
            driver.find_element(By.ID, "petitionerName").send_keys("Patel")
            print("[INFO] Party name entered.")

        captcha_input = wait.until(EC.presence_of_element_located((By.ID, "fcaptcha_code")))
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        print("[INFO] CAPTCHA input set.")

        wait.until(EC.element_to_be_clickable((By.ID, "searchbtn"))).click()
        print("[INFO] Submitted form. Waiting for result content...")

        try:
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "case_details_table"))
            )
            time.sleep(2)

            with open("result_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            try:
                case_details = {
                    "Case Type": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Case Type')]/following-sibling::td").text.strip(),
                    "Filing Number": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Filing Number')]/following-sibling::td").text.strip(),
                    "Filing Date": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Filing Date')]/following-sibling::td").text.strip(),
                    "Registration Number": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Registration Number')]/following-sibling::td").text.strip(),
                    "Registration Date": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'Registration Date')]/following-sibling::td").text.strip(),
                    "CNR Number": driver.find_element(By.XPATH, "//table[contains(@class, 'case_details_table')]//td[contains(text(),'CNR Number')]/following-sibling::td/span").text.strip(),
                }
                data_output["Case Details"] = case_details

            except Exception as e:
                print(f"[ERROR] Case Details extraction: {e}")

            try:
                status_table = driver.find_element(By.XPATH, "//table[contains(@class, 'case_status_table')]")
                rows = status_table.find_elements(By.TAG_NAME, "tr")
                case_status = {
                    "First Hearing Date": rows[0].find_elements(By.TAG_NAME, "td")[1].text.strip(),
                    "Next Hearing Date": rows[1].find_elements(By.TAG_NAME, "td")[1].text.strip(),
                    "Case Stage": rows[2].find_elements(By.TAG_NAME, "td")[1].text.strip(),
                    "Court Number and Judge": rows[3].find_elements(By.TAG_NAME, "td")[1].text.strip()
                }
                data_output["Case Status"] = case_status

            except Exception as e:
                print(f"[ERROR] Case Status extraction: {e}")

            try:
                petitioner = driver.find_element(By.XPATH, "//table[contains(@class, 'Petitioner_Advocate_table')]//td").text.strip()
                data_output["Petitioner and Advocate"] = petitioner
            except Exception as e:
                print(f"[ERROR] Petitioner/Advocate extraction: {e}")

            try:
                respondent = driver.find_element(By.XPATH, "//table[contains(@class, 'Respondent_Advocate_table')]//td").text.strip()
                data_output["Respondent and Advocate"] = respondent
            except Exception as e:
                print(f"[ERROR] Respondent/Advocate extraction: {e}")

            try:
                acts_table = driver.find_element(By.XPATH, "//table[contains(@class, 'acts_table')]")
                rows = acts_table.find_elements(By.TAG_NAME, "tr")
                acts = {
                    "Under Act(s)": rows[1].find_elements(By.TAG_NAME, "td")[0].text.strip(),
                    "Under Section(s)": rows[1].find_elements(By.TAG_NAME, "td")[1].text.strip()
                }
                data_output["Acts"] = acts
            except Exception as e:
                print(f"[ERROR] Acts extraction: {e}")

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
                print(f"[ERROR] Case History extraction: {e}")

        except Exception as e:
            print(f"[ERROR] Case result load: {e}")
            driver.save_screenshot("error_case_page.png")

    else:
        print("[ERROR] CAPTCHA image could not be processed.")

except Exception as e:
    print(f"[FATAL ERROR] {e}")
    driver.save_screenshot("fatal_error.png")

finally:
    driver.quit()
    with open("case_output.json", "w", encoding="utf-8") as f:
        json.dump(data_output, f, indent=4, ensure_ascii=False)
    print("[INFO] Case data saved to case_output.json")
