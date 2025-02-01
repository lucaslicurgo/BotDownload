import telebot
from dotenv import load_dotenv
import os
from yt_dlp import YoutubeDL
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'), parse_mode='HTML')

def progress_hook(d, chat_id, progress_message):
    if d['status'] == 'downloading':
        percent = d['_percent_str']
        speed = d['_speed_str']
        eta = d['eta']

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=progress_message.message_id,
            text=(
                f"Baixando: {percent}\n"
                f"Velocidade: {speed}\n"
                f"Tempo Restante: {eta}s"
            )
        )
    elif d['status'] == 'finished':
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=progress_message.message_id,
            text="Download finalizado. Convertendo..."
        )

@bot.message_handler(commands=['start'])
def welcome_message(message):
    user_name = message.from_user.first_name  or "Usuário"
    welcome_message = (
        f"Olá, seja bem-vindo(a) {user_name} \n"
        "Esse bot é feito para você fazer downloads dos seus vídeos do YouTube"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Fazer Download de um Vídeo", callback_data="video"),
        InlineKeyboardButton("Fazer Download de um aúdio de um vídeo", callback_data="audio"),
        InlineKeyboardButton("Mais opções", callback_data="opcoes")
    )
    try:
        bot.send_message(message.chat.id, welcome_message, reply_markup=markup)
    except Exception as e:
        print(f"Erro ao enviar a mensagem {e}")

@bot.message_handler(commands=['video'])
def download_video(message):
    try:
        link = message.text.split(" ")[1]
        output_file = f"download/{message.chat.id}.mp4"
        chat_id = message.chat.id
        progress_message = bot.send_message(chat_id, 'Iniciando o download...')

        def hook_wrapper(d):
            progress_hook(d, chat_id, progress_message)

        ydl_opts = {
            'format': 'best',
            'outtmpl': output_file,
            'progress_hooks': [hook_wrapper]
        }  
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        with open(output_file, 'rb') as video: 
            bot.send_video(message.chat.id, video, caption='Aqui está seu vídeo!')

        os.remove(output_file)
    except IndexError:
        bot.reply_to(message, "Por favor, envie o comando /download seguido do link que deseja baixar.")
    except Exception as e:
        bot.reply_to(message, f"Erro ao baixar o vídeo: {e}")
        print(e)

@bot.message_handler(commands=['audio'])
def download_audio(message):
    try:
        link = message.text.split(" ")[1]
        chat_id = message.chat.id
        output_file = f"download/{chat_id}"

        progress_message = bot.send_message(chat_id, "Iniciando o download...")

        def hook_wrapper(d):
            progress_hook(d, chat_id, progress_message)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',    
                'preferredquality': '192',
            }],

            'progress_hooks': [hook_wrapper],
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        
        with open(f"{output_file}.mp3", 'rb') as audio:
            bot.send_audio(chat_id, audio, caption='Aqui está o seu aúdio!')
        
        os.remove(f"{output_file}.mp3")
    except IndexError:
        bot.reply_to(message, "Por favor envie o comando /audio seguido do link que deseja baixar.")
    except Exception as e:
        bot.reply_to(message, f"Erro ao baixar o aúdio: {e}")
        print(e)

@bot.callback_query_handler(func=lambda call:True)
def callback_welcome(call):
    if call.data == "video":
        new_message = "Para fazer o Download do Vídeo, preciso que digite /video e o link do vídeo que deseja."
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Voltar", callback_data="voltar")
        )

        try:
            bot.edit_message_text(
                chat_id= call.message.chat.id,
                message_id= call.message.message_id,
                text=new_message,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Erro ao editar a mensagem {e}")

    elif call.data == "audio":
        new_message = "Para fazer o Download do Aúdio, preciso que digite /audio e o link do vídeo que deseja extrair o aúdio."
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Voltar", callback_data="voltar")
        )

        try:
            bot.edit_message_text(
                chat_id = call.message.chat.id,
                message_id=call.message.message_id,
                text=new_message,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Erro ao editar a mensagem {e}")

    elif call.data == "opcoes":
        new_message = "Estamos aprimorando nosso bot a cada dia, aguardem novidades."
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Voltar", callback_data='voltar')
        )

        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id= call.message.message_id,
                text=new_message,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Erro ao editar a mensagem {e}")
        
    elif call.data == "voltar":
        user_name = call.from_user.first_name  or "Usuário"
        welcome_message = (
             f"Olá, seja bem-vindo(a) {user_name} \n"
             "Esse bot é feito para você fazer downloads dos seus vídeos do YouTube"
        )
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Fazer Download de um Vídeo", callback_data="download"),
            InlineKeyboardButton("Mais opções", callback_data="opcoes")
        )
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=welcome_message,
                reply_markup=markup
            )
        except Exception as e:
            print(f"Erro ao enviar a mensagem {e}")

bot.infinity_polling()