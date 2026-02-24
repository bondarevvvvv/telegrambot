import telebot
from telebot import types
import json
import os
import base64
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Вставьте сюда токен вашего бота от @BotFather
BOT_TOKEN = '8510845153:AAGUO5jg01h2NlL46VsD1f-7osYIBVTkxTQ'

bot = telebot.TeleBot(BOT_TOKEN)

# ========== НАСТРОЙКИ АДМИНА ==========
ADMIN_ID = 821500372

SPREADSHEET_ID = '12jDOiE_qD8JySOVgCdpvbPtO-O5RXUmxjSz-C9fS728'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ========== ПОДКЛЮЧЕНИЕ К GOOGLE SHEETS ==========

def get_sheets_client():
    creds_b64 = os.environ.get('GOOGLE_CREDENTIALS_JSON', '')
    creds_json = base64.b64decode(creds_b64).decode('utf-8')
    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)

def get_spreadsheet():
    client = get_sheets_client()
    return client.open_by_key(SPREADSHEET_ID)

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ ==========

def load_data():
    """Загружает всех пользователей из листа Users"""
    try:
        ws = get_spreadsheet().worksheet('Users')
        records = ws.get_all_records()
        data = {}
        for row in records:
            uid = str(row.get('user_id', '')).strip()
            if uid:
                data[uid] = {
                    'name':       row.get('name', ''),
                    'username':   row.get('username', ''),
                    'phone':      row.get('phone', ''),
                    'email':      row.get('email', ''),
                    'question':   row.get('question', ''),
                    'feedback':   row.get('feedback', ''),
                    'created_at': row.get('created_at', ''),
                }
        return data
    except Exception as e:
        print(f"❌ Ошибка загрузки пользователей: {e}")
        return {}

def save_data(data):
    """Сохраняет всех пользователей — используем save_user для каждого"""
    for user_id, user_data in data.items():
        save_user(user_id, user_data)

def save_user(user_id, user_data):
    """Сохраняет или обновляет одного пользователя в листе Users"""
    try:
        ws = get_spreadsheet().worksheet('Users')
        cell = ws.find(str(user_id), in_column=1)

        row_data = [
            str(user_id),
            user_data.get('name', ''),
            user_data.get('username', ''),
            user_data.get('phone', ''),
            user_data.get('email', ''),
            user_data.get('question', ''),
            user_data.get('feedback', ''),
            user_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        ]

        if cell:
            ws.update(f'A{cell.row}:H{cell.row}', [row_data])
        else:
            ws.append_row(row_data)

    except Exception as e:
        print(f"❌ Ошибка сохранения пользователя {user_id}: {e}")

def load_actions():
    """Загружает все действия из листа Actions"""
    try:
        ws = get_spreadsheet().worksheet('Actions')
        return ws.get_all_records()
    except Exception as e:
        print(f"❌ Ошибка загрузки действий: {e}")
        return []

def log_action(user_id, username, first_name, action_type, action_details):
    """Записывает действие пользователя в лист Actions"""
    try:
        ws = get_spreadsheet().worksheet('Actions')
        ws.append_row([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            str(user_id),
            first_name or '',
            username or '',
            action_type,
            str(action_details),
        ])
    except Exception as e:
        print(f"❌ Ошибка записи действия: {e}")

# ========== УВЕДОМЛЕНИЯ АДМИНУ ==========

def notify_admin(title, user_name, user_id, username, details):
    try:
        notification = f"""
🔔 {title}

👤 Пользователь: {user_name}
🆔 ID: {user_id}
📱 Username: @{username if username else 'не указан'}

{details}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Просмотр: /user {user_id}
💬 Ответить: /send {user_id} текст
"""
        bot.send_message(ADMIN_ID, notification)
    except Exception as e:
        print(f"Ошибка отправки уведомления админу: {e}")

def notify_admin_action(user_id, username, first_name, action_type, details):
    try:
        notification = f"""
🔔 ДЕЙСТВИЕ ПОЛЬЗОВАТЕЛЯ

👤 Пользователь: {first_name}
🆔 ID: {user_id}
📱 Username: @{username if username else 'не указан'}

Тип: {action_type}
Детали:
{details}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        bot.send_message(ADMIN_ID, notification)
    except Exception as e:
        print(f"Ошибка отправки уведомления админу: {e}")

# ========== СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЕЙ ==========

user_states = {}

# ========== КЛАВИАТУРА ==========

def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('📋 Обсудить проект')
    btn2 = types.KeyboardButton('📝 Оставить заявку')
    btn3 = types.KeyboardButton('☎️ Контакты')
    btn4 = types.KeyboardButton('💬 Задать вопрос')
    btn5 = types.KeyboardButton('⭐️ Обратная связь')
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    keyboard.add(btn5)
    return keyboard

# ==================== КОМАНДА /START ====================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name

    log_action(user_id, username, first_name, 'command', '/start')
    notify_admin_action(user_id, username, first_name, 'COMMAND', "/start")

    data = load_data()
    is_new_user = user_id not in data

    if is_new_user:
        notify_admin("🆕 НОВЫЙ ПОЛЬЗОВАТЕЛЬ", first_name, user_id, username,
                     "✨ Пользователь впервые запустил бота")
        # Сразу создаём запись в таблице
        save_user(user_id, {
            'name': first_name,
            'username': username or '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

    if user_id in user_states:
        del user_states[user_id]

    text = "Здравствуйте! 👋\nЯ виртуальный помощник проектно-строительной компании\nДельтаСтройПроект.\nПомогу подобрать решение, оставить\nзаявку или связаться с нами!"
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())

# ==================== СООБЩЕНИЕ 2 ====================

@bot.message_handler(func=lambda m: m.text in ["📋 Обсудить проект", "📝 Оставить заявку"])
def message2(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name

    log_action(user_id, username, first_name, 'button_click', message.text)
    notify_admin_action(user_id, username, first_name, 'BUTTON_CLICK', f"Кнопка: {message.text}")

    text = "Расскажите какой у Вас объект?\nМожно выбрать вариант или написать своими словами"

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('🏠 Индивидуальный жилой дом', callback_data='m2_ИЖД')
    btn2 = types.InlineKeyboardButton('🏢 Общественное / коммерческое здание', callback_data='m2_ОКЗ')
    btn3 = types.InlineKeyboardButton('🏫 Образовательное / социальное учреждение', callback_data='m2_ОСУ')
    btn4 = types.InlineKeyboardButton('🏭 Промышленное / складское', callback_data='m2_ПС')
    btn5 = types.InlineKeyboardButton('Другое', callback_data='m2_Другое')
    markup.add(btn1, btn2, btn3, btn4, btn5)

    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== КОНТАКТЫ ====================

@bot.message_handler(func=lambda m: m.text == "☎️ Контакты")
def message28(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name

    log_action(user_id, username, first_name, 'button_click', '☎️ Контакты')

    text = "📍 Контакты проктно-строительной\nкомпании ДельтаСтройПроект\nЕсли у Вас есть вопрос или вы хотите\nобсудить задачу - мы на связи.\n\n 📞 Телефон: +7 (950) 746-77-75\n 💬 Telegram: @lencoln21\n 📧 Email: deltastroyproect@gmail.com"
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())

# ==================== ВСПОМОГАТЕЛЬНЫЕ СООБЩЕНИЯ ====================

def message3(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('🏗 Изменение существующего здания', callback_data='m3_изменение'),
        types.InlineKeyboardButton('🛠 Капитальный ремонт', callback_data='m3_ремонт'),
        types.InlineKeyboardButton('📝 Консультация/не уверен', callback_data='m3_консультация'),
    )
    bot.send_message(chat_id, "Какие работы планируются?", parse_mode='Markdown', reply_markup=markup)

def message4(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('🧱 Затрагивается несущая конструкция', callback_data='m4_несущая'),
        types.InlineKeyboardButton('🏗 Меняются параметры здания', callback_data='m4_параметры'),
        types.InlineKeyboardButton('🛠 Без изменений несущих', callback_data='m4_без_изменений'),
        types.InlineKeyboardButton('🏫 Перестройка/надстройка', callback_data='m4_перестройка'),
        types.InlineKeyboardButton('Другое', callback_data='m4_другое'),
    )
    bot.send_message(chat_id, "Какой масштаб изменений планируется?", parse_mode='Markdown', reply_markup=markup)

def message5(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('📌 Есть четкое ТЗ', callback_data='m5_четкое'),
        types.InlineKeyboardButton('🧠 Есть понимание, но нужно оформить', callback_data='m5_понимание'),
        types.InlineKeyboardButton('💬 Пока на уровне идеи', callback_data='m5_идея'),
        types.InlineKeyboardButton('❓ Сложно сказать', callback_data='m5_сложно'),
    )
    bot.send_message(chat_id, "Насколько у Вас сейчас сформирован запрос?", parse_mode='Markdown', reply_markup=markup)

def message6_and_7(chat_id):
    bot.send_message(chat_id, "Спасибо, я зафиксировал Вашу задачу.\nЧтобы мы могли корректно оценить \nвозможность работы и предложить\nрешение, передам информацию специалисту")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('📞 Телефонный звонок', callback_data='m7_звонок'),
        types.InlineKeyboardButton('💬 Написать в Telegram', callback_data='m7_telegram'),
        types.InlineKeyboardButton('📧 Электронная почта', callback_data='m7_почта'),
        types.InlineKeyboardButton('❓ Пока без связи, хочу задать вопрос', callback_data='m7_вопрос'),
    )
    bot.send_message(chat_id, "Как удобнее продолжить общение?", parse_mode='Markdown', reply_markup=markup)

def message7_1(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('📞 Телефонный звонок', callback_data='m71_звонок'),
        types.InlineKeyboardButton('💬 Написать в Telegram', callback_data='m71_telegram'),
        types.InlineKeyboardButton('📧 Электронная почта', callback_data='m71_почта'),
    )
    bot.send_message(chat_id, "Как удобнее продолжить общение?", parse_mode='Markdown', reply_markup=markup)

def message8(chat_id, user_id, from_feedback=False):
    user_states[user_id] = 'waiting_phone_for_feedback' if from_feedback else 'waiting_phone'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton('📱 Отправить мой номер', request_contact=True))
    bot.send_message(chat_id, "Пожалуйста, оставьте свой номер телефона", reply_markup=keyboard)

def message9(chat_id, user_id):
    if user_id in user_states:
        del user_states[user_id]
    bot.send_message(chat_id, "Спасибо, мы передали информацию специалисту.\nОбычно ответ занимает до 1-2 рабочих\nчасов", reply_markup=get_main_keyboard())

def message10(chat_id, user_id, from_feedback=False):
    user_states[user_id] = 'waiting_email_for_feedback' if from_feedback else 'waiting_email'
    bot.send_message(chat_id, "Укажите электронную почту", reply_markup=types.ReplyKeyboardRemove())

def message11(chat_id, user_id):
    user_states[user_id] = 'waiting_question'
    bot.send_message(chat_id, "Конечно 🙂\nНапишите ваш вопрос - я передам его специалисту", reply_markup=types.ReplyKeyboardRemove())

def message25_and_26(chat_id):
    bot.send_message(chat_id, "Спасибо за сообщение!\nМы предадим его команде.")
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton('📞 Телефон', callback_data='m26_телефон'),
        types.InlineKeyboardButton('💬 Telegram', callback_data='m26_telegram'),
        types.InlineKeyboardButton('📧 Email', callback_data='m26_email'),
        types.InlineKeyboardButton('🔕 Ответ не требуется', callback_data='m26_нет'),
    )
    bot.send_message(chat_id, "Если вы хотите получить ответ, выберите\nудобный способ связи:", parse_mode='Markdown', reply_markup=markup)

def message27(chat_id, user_id):
    if user_id in user_states:
        del user_states[user_id]
    bot.send_message(chat_id, "Спасибо!\nМы учтем Ваше сообщение. Если\nпотребуется, свяжемся с Вами выбранным способ.", reply_markup=get_main_keyboard())

# ==================== ЗАДАТЬ ВОПРОС ====================

@bot.message_handler(func=lambda m: m.text == "💬 Задать вопрос")
def message11_handler(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name

    log_action(user_id, username, first_name, 'button_click', 'Задать вопрос')

    user_states[user_id] = 'waiting_question'
    bot.send_message(message.chat.id, "Конечно 🙂\nНапишите ваш вопрос - я передам его специалисту", reply_markup=types.ReplyKeyboardRemove())

# ==================== ОБРАТНАЯ СВЯЗЬ ====================

@bot.message_handler(func=lambda m: m.text == "⭐️ Обратная связь")
def message24(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name

    log_action(user_id, username, first_name, 'button_click', '⭐️ Обратная связь')

    user_states[user_id] = 'waiting_feedback'
    bot.send_message(message.chat.id, "Нам важно Ваше мнение\nНапишите сообщение = это может быть\nвопрос, комментарий или пожелание.", reply_markup=types.ReplyKeyboardRemove())

# ==================== ОБРАБОТКА КОНТАКТА ====================

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    phone = message.contact.phone_number

    log_action(user_id, username, first_name, 'phone_provided', phone)
    notify_admin("📱 ПОЛУЧЕН ТЕЛЕФОН", first_name, user_id, username,
                 f"☎️ Телефон: {phone}\n\n✅ Контакт отправлен через кнопку")

    # Загружаем, обновляем, сохраняем
    data = load_data()
    if user_id not in data:
        data[user_id] = {}
    data[user_id]['phone'] = phone
    data[user_id]['name'] = first_name
    data[user_id]['username'] = username or ''
    save_user(user_id, data[user_id])  # ← пишем только этого пользователя

    if user_states.get(user_id) == 'waiting_phone_for_feedback':
        message27(message.chat.id, user_id)
    else:
        message9(message.chat.id, user_id)

# ==================== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ====================

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    state = user_states.get(user_id)

    log_action(user_id, username, first_name, 'text_message', message.text)
    notify_admin_action(user_id, username, first_name, 'TEXT_MESSAGE', f"Текст: {message.text}")

    # ---- Ожидание телефона ----
    if state == 'waiting_phone':
        phone = message.text
        log_action(user_id, username, first_name, 'phone_provided', phone)
        notify_admin("📱 ПОЛУЧЕН ТЕЛЕФОН", first_name, user_id, username,
                     f"☎️ Телефон: {phone}\n\n✍️ Написан текстом")
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        data[user_id]['phone'] = phone
        data[user_id]['name'] = first_name
        data[user_id]['username'] = username or ''
        save_user(user_id, data[user_id])
        message9(message.chat.id, user_id)

    # ---- Ожидание email ----
    elif state == 'waiting_email':
        email = message.text
        log_action(user_id, username, first_name, 'email_provided', email)
        notify_admin("📧 ПОЛУЧЕН EMAIL", first_name, user_id, username, f"📧 Email: {email}")
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        data[user_id]['email'] = email
        data[user_id]['name'] = first_name
        data[user_id]['username'] = username or ''
        save_user(user_id, data[user_id])
        message9(message.chat.id, user_id)

    # ---- Ожидание вопроса ----
    elif state == 'waiting_question':
        question = message.text
        log_action(user_id, username, first_name, 'question_asked', question)
        question_preview = question if len(question) < 200 else question[:200] + "..."
        notify_admin("❓ НОВЫЙ ВОПРОС", first_name, user_id, username, f"💬 Вопрос:\n{question_preview}")
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        data[user_id]['question'] = question
        data[user_id]['name'] = first_name
        data[user_id]['username'] = username or ''
        save_user(user_id, data[user_id])
        message9(message.chat.id, user_id)

    # ---- Ожидание обратной связи ----
    elif state == 'waiting_feedback':
        feedback = message.text
        log_action(user_id, username, first_name, 'feedback_provided', feedback)
        feedback_preview = feedback if len(feedback) < 200 else feedback[:200] + "..."
        notify_admin("💬 ОБРАТНАЯ СВЯЗЬ", first_name, user_id, username, f"💭 Сообщение:\n{feedback_preview}")
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        data[user_id]['feedback'] = feedback
        data[user_id]['name'] = first_name
        data[user_id]['username'] = username or ''
        save_user(user_id, data[user_id])
        user_states[user_id] = 'waiting_feedback_choice'
        message25_and_26(message.chat.id)

    # ---- Ожидание телефона для обратной связи ----
    elif state == 'waiting_phone_for_feedback':
        phone = message.text
        log_action(user_id, username, first_name, 'phone_for_feedback', phone)
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        data[user_id]['phone'] = phone
        save_user(user_id, data[user_id])
        message27(message.chat.id, user_id)

    # ---- Ожидание email для обратной связи ----
    elif state == 'waiting_email_for_feedback':
        email = message.text
        log_action(user_id, username, first_name, 'email_for_feedback', email)
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        data[user_id]['email'] = email
        save_user(user_id, data[user_id])
        message27(message.chat.id, user_id)

# ==================== ОБРАБОТКА INLINE-КНОПОК ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    username = call.from_user.username
    first_name = call.from_user.first_name

    log_action(user_id, username, first_name, 'inline_button_click', call.data)
    notify_admin_action(user_id, username, first_name, 'INLINE_BUTTON', f"Кнопка: {call.data}")

    bot.answer_callback_query(call.id)

    if call.data.startswith('m2_'):
        object_type = call.data.replace('m2_', '')
        notify_admin("📝 НАЧАЛО ОФОРМЛЕНИЯ ЗАЯВКИ", first_name, user_id, username,
                     f"🏗 Тип объекта: {object_type}\n\n📋 Пользователь начал оформлять заявку")
        message3(chat_id)

    elif call.data == 'm3_изменение':
        message4(chat_id)
    elif call.data == 'm3_ремонт':
        message5(chat_id)
    elif call.data == 'm3_консультация':
        message7_1(chat_id)

    elif call.data.startswith('m4_'):
        message5(chat_id)

    elif call.data.startswith('m5_'):
        message6_and_7(chat_id)

    elif call.data == 'm7_звонок':
        message8(chat_id, user_id)
    elif call.data == 'm7_telegram':
        message9(chat_id, user_id)
    elif call.data == 'm7_почта':
        message10(chat_id, user_id)
    elif call.data == 'm7_вопрос':
        message11(chat_id, user_id)

    elif call.data == 'm71_звонок':
        message8(chat_id, user_id)
    elif call.data == 'm71_telegram':
        message9(chat_id, user_id)
    elif call.data == 'm71_почта':
        message10(chat_id, user_id)

    elif call.data == 'm26_телефон':
        message8(chat_id, user_id, from_feedback=True)
    elif call.data == 'm26_telegram':
        message27(chat_id, user_id)
    elif call.data == 'm26_email':
        message10(chat_id, user_id, from_feedback=True)
    elif call.data == 'm26_нет':
        message27(chat_id, user_id)

# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    print("🤖 Основной бот запущен...")
    print(f"📢 Уведомления отправляются админу ID: {ADMIN_ID}")
    bot.remove_webhook()
    bot.infinity_polling()
