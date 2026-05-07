import time
import schedule
import requests
import urllib.parse
from datetime import datetime

# --- CONFIG ---
# നിന്റെ നമ്പർ മാത്രം ഇവിടെ നൽകുക
MY_PHONE = "971551347989" 
API_KEY = "7463030"

def send_reminder(task):
    message = f"🔔 *FAISAL, DON'T FORGET!*\n\n📝 Task: {task}\n⏰ Time: {datetime.now().strftime('%I:%M %p')}"
    encoded_msg = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={MY_PHONE}&text={encoded_msg}&apikey={API_KEY}"
    
    try:
        requests.get(url, timeout=10)
        print(f"Reminder sent: {task}")
    except Exception as e:
        print(f"Error: {e}")

# --- റിമൈൻഡറുകൾ ഇവിടെ സെറ്റ് ചെയ്യാം ---
# ഉദാഹരണത്തിന്:

# 1. എന്നും രാത്രി 9 മണിക്ക് ഓയിൽ പ്രൈസ് നോക്കാൻ
schedule.every().day.at("21:00").do(send_reminder, task="Check Crude Oil Inventory & Price")

# 2. ദിവസവും രാവിലെ 8 മണിക്ക് ട്രേഡിംഗ് പ്ലാൻ തയ്യാറാക്കാൻ
schedule.every().day.at("08:00").do(send_reminder, task="Prepare Nifty Trading Plan")

# 3. വെള്ളിയാഴ്ച മാത്രം വരുന്ന റിമൈൻഡർ
schedule.every().friday.at("10:00").do(send_reminder, task="Weekly Profit/Loss Review")

print("Smart Reminder Bot is running...")

while True:
    schedule.run_pending()
    time.sleep(60) # ഓരോ മിനിറ്റിലും ചെക്ക് ചെയ്യും
