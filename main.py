import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import requests
import urllib.request
import os
import openai
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHATPDF_API_KEY = os.getenv('CHATPDF_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_video(video_url):
    # Use OpenAI to generate a summary
    response = openai.Completion.create(
        engine="davinci",  # Or another suitable engine
        prompt=f'Summarize deeply the main points of the video: {video_url}.',
        max_tokens=150,    # Adjust as needed
        n=1,               # Number of completions    # Define a stop condition
    )

    summary = response.choices[0].text.strip()
    return summary

# video_url = "https://youtu.be/Q9zv369Ggfk?si=LGG8qHk_sOG1smI3"
# summary = summarize_video(video_url)
# print(summary)

#!IMPORTANT!
#USED FOR DOCS UPLOAD
# headers = {'x-api-key': CHATPDF_API_KEY,'Content-Type': 'application/json'
#     }
# data = {'url':'https://hackathon.fra1.cdn.digitaloceanspaces.com/compsci.pdf'}
# response = requests.post('https://api.chatpdf.com/v1/sources/add-url', headers=headers, json=data)
# if response.status_code == 200:
#     print('Source ID:', response.json()['sourceId'])
# else:
#     print('Status:', response.status_code)
#     print('Error:', response.text)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_choices = {}
user_info = []

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text="Welcome to NISAI - your faithful companion on the path to successful learning! ... (your message here)",
        reply_markup=ReplyKeyboardMarkup([["sat", "ielts"], ["igcse", "compsci", "physics", "math"]], one_time_keyboard=True)
    )

def button(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_choice = update.message.text

    user_choices[user_id] = user_choice
    user_info.append(user_choice)

    if user_choice in ["compsci", "physics", "math"]:
        context.bot.send_message(
            chat_id=user_id,
            text="Please choose your grade:",
            reply_markup=ReplyKeyboardMarkup([["7", "8", "9"], ["10", "11", "12"]], one_time_keyboard=True)
        )
    elif user_choice in ["igcse"]:
        context.bot.send_message(
            chat_id=user_id,
            text="Please choose your grade:",
            reply_markup=ReplyKeyboardMarkup([["10"], ["11"], ["12"]], one_time_keyboard=True)
        )
    else:
        context.bot.send_message(
            chat_id=user_id,
            text="Please choose your grade:",
            reply_markup=ReplyKeyboardMarkup([["11"], ["12"]], one_time_keyboard=True)
        )

def grade_choice(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    grade = update.message.text

    user_choices[user_id] = grade
    user_info.append(grade)
    context.bot.send_message(
        chat_id=user_id,
        text = "in grade choice"
    )

    context.bot.send_message(
        chat_id=user_id,
        text="What would you like to do2?",
        reply_markup=ReplyKeyboardMarkup([["Ask a Question", "Send Me a Book", "Mock SA", "Summarize youtube video"]], one_time_keyboard=True)
    )

def option_choice(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    option = update.message.text

    user_choices[user_id] = option
    user_info.append(option)
    print(user_info)

    if option == "Ask a Question":
        context.bot.send_message(
            chat_id=user_id,
            text="Please ask your question."
        )
    elif option == "Send Me a Book":
        print(user_info)
        pdf_url = 'https://hackathon.fra1.cdn.digitaloceanspaces.com/'
        pdf_url += user_info[0]
        pdf_url += '%20'
        pdf_url += user_info[1]
        pdf_url += '.pdf'
        pdf_file = os.path.basename(pdf_url)
        print(pdf_url)

        urllib.request.urlretrieve(pdf_url, pdf_file)

        context.bot.send_document(
            chat_id=user_id,
            document=open(pdf_file, 'rb')
        )

        os.remove(pdf_file) 
    elif option == "Mock SA":
        context.bot.send_message(
            chat_id=user_id,
            text="What is your unit?"
        )
    elif option == "Summarize youtube video":
        context.bot.send_message(
            chat_id=user_id,
            text="Send me a youtube link"
        )
    else:
        context.bot.send_message(
            chat_id=user_id,
            text="Invalid option. Please choose 'Ask a Question' or 'Send Me a Book' or 'Mock SA' or 'Summarize youtube video'."
        )

def handle_user_question(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    question = update.message.text
    
    if user_info[2] == "Ask a Question":
        headers = {
            'x-api-key': CHATPDF_API_KEY,
            "Content-Type": "application/json",
        }

        data = {
            'sourceId': "src_zPnOPw7uqOgGY9T3o9cwg",
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
    elif user_info[2] == "Mock SA":
        headers = {
            'x-api-key': CHATPDF_API_KEY,
            "Content-Type": "application/json",
        }

        data = {
            'sourceId': "src_zPnOPw7uqOgGY9T3o9cwg",
            'messages': [
                {
                    'role': "user",
                    'content': "Using the PDF book you have, create 10 question exam on this topic:" + question,
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
    elif user_info[2] == "Summarize youtube video":
        video_url = question
        summary = summarize_video(video_url)
        context.bot.send_message(
        chat_id=user_id,
        text = summary
        )

button_handler = MessageHandler(Filters.regex(r'^(compsci|physics|math|igcse|sat|ielts)$'), button)
grade_handler = MessageHandler(Filters.regex(r'^(7|8|9|10|11|12)$'), grade_choice)

if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    option_handler = MessageHandler(Filters.regex(r'^(Ask a Question|Send Me a Book|Mock SA|Summarize youtube video)$'), option_choice)
    question_handler = MessageHandler(Filters.text & ~Filters.command, handle_user_question)

    dp.add_handler(start_handler)
    dp.add_handler(button_handler)
    dp.add_handler(grade_handler)
    dp.add_handler(option_handler)
    dp.add_handler(question_handler)

    updater.start_polling()
    updater.idle()
