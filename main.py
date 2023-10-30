import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import requests

# headers = {'x-api-key': 'sec_BBiFx587OnD7EOedplwQIpfPrjqZLp34','Content-Type': 'application/json'
#     }
# data = {'url':'https://www.africau.edu/images/default/sample.pdf'}

# response = requests.post('https://api.chatpdf.com/v1/sources/add-url', headers=headers, json=data)

# if response.status_code == 200:
#     print('Source ID:', response.json()['sourceId'])
# else:
#     print('Status:', response.status_code)
#     print('Error:', response.text)

TELEGRAM_TOKEN = '6425414932:AAE3p4gNl_eJqPc3D9FWWxtVmP1sDE6NiSo'
# chatpdf = chatpdf.ChatPDF('sec_BBiFx587OnD7EOedplwQIpfPrjqZLp34')
# chatpdf.load_pdf('https://drive.google.com/file/d/1-O8d_RjRsRTQg4v-Jqb39SQy9cZXfIU3/view?usp=sharing')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_choices = {}

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text="Welcome to NISAI - your faithful companion on the path to successful learning! ... (your message here)",
        reply_markup=ReplyKeyboardMarkup([["SAT", "IELTS"], ["IGCSE", "CompSci", "Physics", "Math"]], one_time_keyboard=True)
    )

def button(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_choice = update.message.text

    user_choices[user_id] = user_choice

    if user_choice in ["CompSci", "Physics", "Math"]:
        context.bot.send_message(
            chat_id=user_id,
            text="Please choose your grade:",
            reply_markup=ReplyKeyboardMarkup([["7", "8", "9"], ["10", "11", "12"]], one_time_keyboard=True)
        )
    else:
        context.bot.send_message(
            chat_id=user_id,
            text="What would you like to do1?",
            reply_markup=ReplyKeyboardMarkup([["Ask a Question", "Book"]], one_time_keyboard=True)
        )

def grade_choice(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    grade = update.message.text
    
    user_choices[user_id] = grade
    context.bot.send_message(
        chat_id=user_id,
        text = "in grade choice"
    )

    context.bot.send_message(
        chat_id=user_id,
        text="What would you like to do2?",
        reply_markup=ReplyKeyboardMarkup([["Ask a Question", "Book"]], one_time_keyboard=True)
    )

def option_choice(update: Update, context: CallbackContext):

    user_id = update.effective_user.id
    option = update.message.text

    print(option)

    first_choice = user_choices.get(user_id)

    if option == "Ask a Question":
        context.bot.send_message(
            chat_id=user_id,
            text="Please ask your question."
        )
        # Save the user's choice to ask a question for later processing
        user_choices[user_id] += " Ask a Question "
    elif option == "Book":
        # Do something with the choice of "Book"
        pass
    else:
        context.bot.send_message(
            chat_id=user_id,
            text="Invalid option. Please choose 'Ask a Question' or 'Book'."
        )

def handle_user_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    question = update.message.text

    headers = {
        'x-api-key': 'sec_BBiFx587OnD7EOedplwQIpfPrjqZLp34',
        "Content-Type": "application/json",
    }

    data = {
        'sourceId': "src_4BP4R4ShoALkecBsruvrA",
        'messages': [
            {
                'role': "user",
                'content': question,
            }
        ]
    }

    response = requests.post(
        'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)

    if response.status_code == 200:
        print('Result:', response.json()['content'])
        res = response.json()['content']
    else:
        print('Status:', response.status_code)
        print('Error:', response.text)

    context.bot.send_message(
        chat_id=user_id,
        text=res
    )


# ...

# Separate message handlers for button choice and grade choice
button_handler = MessageHandler(Filters.regex(r'^(CompSci|Physics|Math)$'), button)
grade_handler = MessageHandler(Filters.regex(r'^(7|8|9|10|11|12)$'), grade_choice)

# ...

if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    option_handler = MessageHandler(Filters.regex(r'^(Ask a Question|Book)$'), option_choice)
    question_handler = MessageHandler(Filters.text & ~Filters.command, handle_user_question)

    dp.add_handler(start_handler)
    dp.add_handler(button_handler)  # Handles subject choices (e.g., CompSci, Physics, Math)
    dp.add_handler(grade_handler)   # Handles grade choices (e.g., 7, 8, 9, 10, 11, 12)
    dp.add_handler(option_handler)  # Handles "Ask a Question" and "Book" options
    dp.add_handler(question_handler) # Handles user questions

    updater.start_polling()
    updater.idle()
