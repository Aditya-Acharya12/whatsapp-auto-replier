from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os
import random
import hashlib
from llm import get_llm_reply

CHROME_DRIVER_PATH = 'chromedriver.exe'  # Adjust path if needed

#Hash function to track seen messages
def hash_msg(msg):
    return hashlib.md5(msg.encode('utf-8')).hexdigest()

#Strip unsupported characters (like emojis)
def strip_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

#Launch Chrome with WhatsApp
def open_whatsapp():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-gpu")
    options.add_argument(r"--user-data-dir=C:\Users\adity\OneDrive\Desktop\whatsapp-bot\profile")

    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
    driver.get('https://web.whatsapp.com')

    print("Waiting for QR Code scan...")

    # Wait for login
    while True:
        try:
            driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
            break
        except:
            time.sleep(2)
    print("Login successful.")
    return driver

# Get last N incoming messages
def get_last_n_messages(driver, n=3):
    try:
        messages = driver.find_elements(
            By.XPATH,
            '//div[contains(@class, "message-in")]'
        )
        if not messages:
            return []

        last_n = messages[-n:]
        texts = []
        for msg in last_n:
            spans = msg.find_elements(By.XPATH, './/span[contains(@class, "selectable-text")]/span')
            if spans:
                texts.append(spans[-1].text)
        return texts
    except Exception as e:
        print("Error getting last N messages:", e)
        return []

# MAIN LOOP
if __name__ == "__main__":
    driver = open_whatsapp()
    input("Press Enter after you've opened the target chat manually...\n")
    print("Listening for new messages...\n")

    last_seen_hash = None
    last_reply_time = 0
    REPLY_COOLDOWN = 20 

    seen_hashes = set()

    while True:
        try:
            messages = get_last_n_messages(driver, n=4)  # Increased to 4 for context

            if not messages:
                time.sleep(2)
                continue

            latest_msg = messages[-1].strip()
            if not latest_msg:
                time.sleep(2)
                continue

            latest_hash = hash_msg(latest_msg)
            
            # ✅ Already seen this message — skip
            if latest_hash == last_seen_hash:
                time.sleep(2)
                continue

            # ✅ Wait for user to send at least 2 new messages before replying
            if len(set(messages[-2:])) < 2:
                time.sleep(2)
                continue

            # ✅ Enforce cooldown between replies
            if time.time() - last_reply_time < REPLY_COOLDOWN:
                time.sleep(2)
                continue

            last_seen_hash = latest_hash
            last_reply_time = time.time()

            context = "\n".join(messages[-3:])  # Use 3 messages for context
            reply = get_llm_reply(latest_msg, context)

            # ✅ Limit reply length to 2 lines or 25 words max
            words = reply.strip().split()
            if len(words) > 25:
                reply = " ".join(words[:25]) + "..."

            safe_reply = strip_non_bmp(reply)

            print("Replying with:", safe_reply)

            input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            input_box.click()

            for c in safe_reply:
                input_box.send_keys(c)
                time.sleep(random.uniform(0.03, 0.08))  # simulate typing

            input_box.send_keys("\n")  # press Enter to send
            time.sleep(random.uniform(1.5, 3.5))  # cool-off time

        except Exception as e:
            print("Error:", e)
            time.sleep(3)
