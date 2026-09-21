import pyautogui
import pyperclip
import time

MESSAGE = "Automated test message"
COUNT = 100
DELAY = 0.5

print("=" * 50)
print("1. Move your mouse over WhatsApp's message box.")
print("2. DO NOT TOUCH anything once the countdown begins.")
print("=" * 50)

for i in range(5, 0, -1):
    print(f"Starting in {i} seconds... (Keep cursor over WhatsApp)")
    time.sleep(1)

# Forces focus onto WhatsApp by clicking where your cursor currently sits
pyautogui.click()
time.sleep(0.5)

print("\n>>> SENDING MESSAGES NOW <<<")

for i in range(COUNT):
    pyperclip.copy(f"{MESSAGE} #{i + 1}")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    time.sleep(DELAY)

print("\nDone!")