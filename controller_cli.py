import subprocess
import json
import os
import time
import signal
import platform

BOT_STATE_FILE = "bot_state.json"
bot_process = None  # Global handle to the bot process

venv_python = os.path.join(os.environ['VIRTUAL_ENV'], 'Scripts', 'python.exe') if os.getenv("VIRTUAL_ENV") else "python"

def set_bot_state(enabled: bool):
    with open(BOT_STATE_FILE, "w") as f:
        json.dump({"enabled": enabled}, f, indent=2)

def start_bot():
    global bot_process
    if bot_process is None:
        venv_python = os.path.join(os.environ['VIRTUAL_ENV'], 'Scripts', 'python.exe') if os.getenv("VIRTUAL_ENV") else "python"

        bot_process = subprocess.Popen(
            [
                "cmd", "/c", "start", "cmd", "/k", f"{venv_python} main.py"
            ],
            shell=True
        )
        print("✅ Bot started in a new terminal window.\n")
    else:
        print("⚠️ Bot is already running.\n")



def pause_bot():
    set_bot_state(False)
    print("⏸️ Bot paused.\n")

def resume_bot():
    set_bot_state(True)
    print("▶️ Bot resumed.\n")

def stop_bot():
    try:
        with open("bot_pid.txt", "r") as f:
            pid = int(f.read().strip())

        subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
        print("🛑 Bot stopped.\n")

    except FileNotFoundError:
        print("⚠️ No running bot found (bot_pid.txt missing).\n")
    except Exception as e:
        print(f"⚠️ Error stopping bot: {e}\n")


if __name__ == "__main__":
    print("📟 WhatsApp Bot CLI Controller")
    print("Commands: start, pause, resume, exit\n")

    while True:
        cmd = input(">>> ").strip().lower()

        if cmd == "start":
            start_bot()
        elif cmd == "pause":
            pause_bot()
        elif cmd == "resume":
            resume_bot()
        elif cmd == "exit":
            stop_bot()
            print("👋 Exiting CLI.\n")
            break
        else:
            print("❓ Unknown command. Try: start, pause, resume, exit\n")
