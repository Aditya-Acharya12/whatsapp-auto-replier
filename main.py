from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
import hashlib
from llm import get_llm_reply
import json

CHROME_DRIVER_PATH = 'chromedriver.exe'  # Adjust path if needed

# Hash function to track seen messages
def hash_msg(msg):
    return hashlib.md5(msg.encode('utf-8')).hexdigest()

# Strip unsupported characters (like emojis)
def strip_non_bmp(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

def is_bot_enabled():
    try:
        with open("bot_state.json", "r") as f:
            state = json.load(f)
        return state.get("enabled", False)
    except Exception:
        return False  # Default to paused if file not found or error

# Launch Chrome with WhatsApp
def open_whatsapp():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-gpu")
    options.add_argument(r"--user-data-dir=C:\Users\adity\OneDrive\Desktop\whatsapp-bot\profile")

    service = Service(
        CHROME_DRIVER_PATH,
        log_path=os.devnull  # hides chromedriver logs
    )

    options.add_argument("--log-level=3")  # Suppress most logs

    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://web.whatsapp.com')

    print("Waiting for QR Code scan...")
    while True:
        try:
            driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
            break
        except:
            time.sleep(2)

    print("Login successful.")
    return driver

def load_whitelist():
    try:
        with open("whitelist.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def get_recent_chats(driver):
    chat_elements = driver.find_elements(By.XPATH, '//div[@data-testid="cell-frame-container"]')
    return chat_elements

def get_chat_name(chat_element):
    try:
        name_span = chat_element.find_element(By.XPATH, './/span[@dir="auto"]')
        return name_span.text.strip()
    except:
        return ""

def open_chat(chat_element):
    try:
        chat_element.click()
        time.sleep(2)  # wait for chat to load
        return True
    except Exception as e:
        print("Couldn't open chat:", e)
        return False

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

if __name__ == "__main__":
    # Write current PID to file
    with open("bot_pid.txt", "w") as f:
        f.write(str(os.getpid()))

    try:
        driver = open_whatsapp()
        whitelist = load_whitelist()
        print("✅ Loaded whitelist:", whitelist)
        print("Listening for new messages...\n")

        last_seen_hash = None
        last_reply_time = 0
        REPLY_COOLDOWN = 20

        while True:
            try:
                if not is_bot_enabled():
                    print("⏸️ Bot is paused. Waiting to resume...")
                    time.sleep(2)
                    continue

                # Wait for sidebar chats to load
                try:
                    print("⏳ Waiting for sidebar chats to load...")
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@role="gridcell"]'))
                    )
                    recent_chats = driver.find_elements(By.XPATH, '//div[@role="gridcell"]')
                    print(f"🔍 Found {len(recent_chats)} chats in sidebar")

                except Exception as e:
                    print("❌ Sidebar chats not found:", e)
                    recent_chats = []


                for chat in recent_chats:
                    try:
                        name_element = chat.find_element(By.XPATH, './/span[@dir="auto" and @title]')
                        chat_name = name_element.get_attribute("title")
                        print(f"➡️ Chat name: {chat_name}")

                        if chat_name not in whitelist:
                            print(f"⛔ Skipping {chat_name} — not in whitelist")
                            continue

                        print(f"✅ Scanning chat with {chat_name}")
                        if not open_chat(chat):
                            continue

                        messages = get_last_n_messages(driver, n=4)
                        if not messages:
                            continue

                        latest_msg = messages[-1].strip()
                        if not latest_msg:
                            continue

                        latest_hash = hash_msg(latest_msg)
                        if latest_hash == last_seen_hash:
                            continue

                        if len(set(messages[-2:])) < 2:
                            continue

                        if time.time() - last_reply_time < REPLY_COOLDOWN:
                            continue

                        # Passed all filters, time to reply
                        last_seen_hash = latest_hash
                        last_reply_time = time.time()

                        context = "\n".join(messages[-3:])
                        reply = get_llm_reply(latest_msg, context)

                        words = reply.strip().split()
                        if len(words) > 25:
                            reply = " ".join(words[:25]) + "..."

                        safe_reply = strip_non_bmp(reply)
                        print(f"💬 Replying to {chat_name}: {safe_reply}")

                        input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                        input_box.click()
                        for c in safe_reply:
                            input_box.send_keys(c)
                            time.sleep(random.uniform(0.03, 0.08))
                        input_box.send_keys("\n")
                        time.sleep(random.uniform(1.5, 3.5))
                    except Exception as e:
                        print(f"❌ Error processing chat: {e}")
                        continue

                time.sleep(3)

            except Exception as e:
                print("Error:", e)
                time.sleep(3)

    finally:
        if os.path.exists("bot_pid.txt"):
            os.remove("bot_pid.txt")
