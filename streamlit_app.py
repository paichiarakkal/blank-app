import os
import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# ----------------------------------------------------
# 1. Google Sheets Setup
# ----------------------------------------------------
# Google Sheets API പ്രമാണങ്ങൾ ഫോൾഡറിൽ ഉണ്ടെന്ന് ഉറപ്പാക്കുക
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# നിങ്ങളുടെ Google Sheet പേര് ഇവിടെ നൽകുക
sheet = client.open("Paichi Expenses").sheet1


# ----------------------------------------------------
# 2. Helper Functions
# ----------------------------------------------------
def get_current_balance():
    """ഗൂഗിൾ ഷീറ്റിൽ നിന്ന് ടോട്ടൽ ബാലൻസ് കണക്കാക്കുന്നു"""
    try:
        records = sheet.get_all_records()
        total_income = 0
        total_expense = 0

        for row in records:
            # നിങ്ങളുടെ ഷീറ്റിലെ കോളം പേരുകൾക്കനുസരിച്ച് ഇവ മാറ്റാം (Amount, Type / Expense)
            amount = float(row.get('Amount', 0))
            trans_type = str(row.get('Type', '')).lower()

            if trans_type in ['income', 'credit', 'c', 'വരവ്']:
                total_income += amount
            else:
                total_expense += amount

        balance = total_income - total_expense
        return balance, total_income, total_expense
    except Exception as e:
        print(f"Error calculating balance: {e}")
        return 0, 0, 0


def parse_expense_msg(msg_text):
    """സാധാരണ മെസ്സേജിൽ നിന്ന് Item, Amount, Type എന്നിവ വേർതിരിക്കുന്നു"""
    # ഉദാഹരണത്തിന്: "Admisab 3302 c" അല്ലെങ്കിൽ "Rice 500"
    match = re.search(r'^(.*?)\s+(\d+(?:\.\d+)?)\s*([cC]?)$', msg_text)
    if match:
        item = match.group(1).strip()
        amount = float(match.group(2))
        is_credit = match.group(3).lower() == 'c'
        trans_type = 'Income' if is_credit else 'Expense'
        return item, amount, trans_type
    else:
        return msg_text, 0, 'Expense'


# ----------------------------------------------------
# 3. WhatsApp Webhook Route
# ----------------------------------------------------
@app.route("/webhook", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.form.get('Body', '').strip()
    sender_name = request.form.get('ProfileName', 'User')
    
    resp = MessagingResponse()
    msg = resp.message()

    # ------------------------------------------------
    # CASE 1: Balance Check Command
    # ------------------------------------------------
    if incoming_msg.lower() in ['balance', 'ബാലൻസ്', 'bal']:
        balance, income, expense = get_current_balance()
        reply_text = (
            f"📊 *PAICHI EXPENSES STATEMENT*\n\n"
            f"💵 Total Income: ₹{income:,.2f}\n"
            f"💸 Total Expense: ₹{expense:,.2f}\n"
            f"---------------------------\n"
            f"💰 *Current Balance: ₹{balance:,.2f}*"
        )
        msg.body(reply_text)
        return str(resp)

    # ------------------------------------------------
    # CASE 2: New Transaction Entry
    # ------------------------------------------------
    item, amount, trans_type = parse_expense_msg(incoming_msg)

    # Google Sheet-ലേക്ക് എന്റ്രി ചേർക്കുന്നു
    try:
        sheet.append_row([item, amount, trans_type, sender_name])
        reply_text = (
            f"✅ *Entry Saved!*\n"
            f"Item: {item}\n"
            f"Amount: ₹{amount}\n"
            f"Type: {trans_type}\n"
            f"By: {sender_name}"
        )
    except Exception as e:
        reply_text = f"❌ Error saving entry: {str(e)}"

    msg.body(reply_text)
    return str(resp)


# ----------------------------------------------------
# 4. Main App Runner
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)