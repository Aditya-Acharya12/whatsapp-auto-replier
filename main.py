from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os

CHROME_DRIVER_PATH = 'chromedriver.exe'  # Path to your ChromeDriver executable

def open_whatsapp():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-gpu")
    # options.add_argument("--headless=new") 
    options.add_argument(r"--user-data-dir=C:\Users\adity\OneDrive\Desktop\whatsapp-bot\profile")

    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
    driver.get('https://web.whatsapp.com')

    print("Waiting for QR Code scan...")

    # Wait until login is detected
    try:
        while True:
            try:
                driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
                break
            except:
                time.sleep(2)
        print("Login successful.")
    except Exception as e:
        print("Error during login check:", e)

    return driver

def get_last_message(driver):
    try:
        messages = driver.find_elements(
            By.XPATH,
            '//div[contains(@class, "message-in") or contains(@class, "message-out")]'
        )

        if not messages:
            return None

        last_msg = messages[-1]
        text_spans = last_msg.find_elements(By.XPATH, './/span[contains(@class, "selectable-text")]/span')

        if text_spans:
            return text_spans[-1].text
        else:
            return "[Media or emoji message]"

    except Exception as e:
        print("Error getting last message:", e)
        return None

if __name__ == "__main__":
    driver = open_whatsapp()
    input("Press Enter after you've opened the target chat manually...")
    print("Listening for new messages...")

    last_seen = None

    while True:
        msg = get_last_message(driver)
        if msg and msg != last_seen:
            print("New message:", msg)
            last_seen = msg
        time.sleep(2)
