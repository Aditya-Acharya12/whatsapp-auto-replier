from selenium import webdriver   # for web automation
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time # to pause execution

CHROME_DRIVER_PATH = 'chromedriver.exe' # Path to your ChromeDriver executable

def open_whatsapp():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless=new")  # optional: remove this if you want to SEE Chrome
    options.add_argument(r"--user-data-dir=C:\Users\adity\OneDrive\Desktop\whatsapp-bot\profile")


    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)  # launches Chrome

    driver.get('https://web.whatsapp.com')
    print("Waiting for QR Code scan...")

    # Wait until main UI appears
    try:
        search_box = None
        while not search_box:
            time.sleep(2)
            try:
                search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            except:
                pass
        print("Login successful.")
    except Exception as e:
        print("Error during login check:", e)

    return driver

if __name__ == "__main__":
    driver = open_whatsapp()
    input("Press Enter after you've opened the target chat manually...")