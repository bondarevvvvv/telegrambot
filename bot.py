import telebot
from telebot import types
import json
import os
from datetime import datetime

# Вставьте сюда токен вашего бота от @BotFather
BOT_TOKEN = '8510845153:AAGUO5jg01h2NlL46VsD1f-7osYIBVTkxTQ'

bot = telebot.TeleBot(BOT_TOKEN)

# ========== НАСТРОЙКИ АДМИНА ==========
ADMIN_ID = 821500372  # ← ВСТАВЬТЕ ВАШЕ ID СЮДА!

# Функция отправки уведомления админу
def notify_admin(title, user_name, user_id, username, details):
    """Отправляет уведомление админу о действии пользователя"""
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

# Файл для хранения данных
DATA_FILE = 'users_data.json'
ACTIONS_FILE = 'user_actions.json'

# Загрузка данных
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Сохранение данных
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Загрузка действий
def load_actions():
    if os.path.exists(ACTIONS_FILE):
        with open(ACTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Сохранение действий
def save_actions(actions):
    with open(ACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(actions, f, ensure_ascii=False, indent=2)

# Функция для записи действия пользователя
def log_action(user_id, username, first_name, action_type, action_details):
    actions = load_actions()
    
    action = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'action_type': action_type,
        'action_details': action_details
    }
    
    actions.append(action)
    save_actions(actions)

# Словарь для отслеживания состояния пользователей
user_states = {}

# Функция для создания постоянной клавиатуры внизу
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
    
    # Логируем действие
    log_action(user_id, username, first_name, 'command', '/start')
    
    # Проверяем новый ли пользователь
    data = load_data()
    is_new_user = user_id not in data
    
    if is_new_user:
        notify_admin(
            "🆕 НОВЫЙ ПОЛЬЗОВАТЕЛЬ",
            first_name,
            user_id,
            username,
            "✨ Пользователь впервые запустил бота"
        )
    
    # Сбрасываем состояние при старте
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
    
    # Логируем действие
    log_action(user_id, username, first_name, 'button_click', message.text)
    
    text = "Расскажите какой у Вас объект?\nМожно выбрать вариант или написать своими словами"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('🏠 Индивидуальный жилой дом', callback_data='m2_ИЖД')
    btn2 = types.InlineKeyboardButton('🏢 Общественное / коммерческое здание', callback_data='m2_ОКЗ')
    btn3 = types.InlineKeyboardButton('🏫 Образовательное / социальное учреждение', callback_data='m2_ОСУ')
    btn4 = types.InlineKeyboardButton('🏭 Промышленное / складское', callback_data='m2_ПС')
    btn5 = types.InlineKeyboardButton('Другое', callback_data='m2_Другое')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== СООБЩЕНИЕ 28 (Контакты) ====================

@bot.message_handler(func=lambda m: m.text == "☎️ Контакты")
def message28(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Логируем действие
    log_action(user_id, username, first_name, 'button_click', '☎️ Контакты')
    
    text = "📍 Контакты проктно-строительной\nкомпании ДельтаСтройПроект\nЕсли у Вас есть вопрос или вы хотите\nобсудить задачу - мы на связи.\n\n 📞 Телефон: +7 (950) 746-77-75\n 💬 Telegram: @lencoln21\n 📧 Email: deltastroyproect@gmail.com"
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())

# ==================== СООБЩЕНИЕ 3 ====================

def message3(chat_id):
    text = "Какие работы планируются?"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('🏗 Изменение существующего здания', callback_data='m3_изменение')
    btn2 = types.InlineKeyboardButton('🛠 Капитальный ремонт', callback_data='m3_ремонт')
    btn3 = types.InlineKeyboardButton('📝 Консультация/не уверен', callback_data='m3_консультация')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== СООБЩЕНИЕ 4 ====================

def message4(chat_id):
    text = "Какой масштаб изменений планируется?"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('🧱 Затрагивается несущая конструкция', callback_data='m4_несущая')
    btn2 = types.InlineKeyboardButton('🏗 Меняются параметры здания', callback_data='m4_параметры')
    btn3 = types.InlineKeyboardButton('🛠 Без изменений несущих', callback_data='m4_без_изменений')
    btn4 = types.InlineKeyboardButton('🏫 Перестройка/надстройка', callback_data='m4_перестройка')
    btn5 = types.InlineKeyboardButton('Другое', callback_data='m4_другое')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== СООБЩЕНИЕ 5 ====================

def message5(chat_id):
    text = "Насколько у Вас сейчас сформирован запрос?"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('📌 Есть четкое ТЗ', callback_data='m5_четкое')
    btn2 = types.InlineKeyboardButton('🧠 Есть понимание, но нужно оформить', callback_data='m5_понимание')
    btn3 = types.InlineKeyboardButton('💬 Пока на уровне идеи', callback_data='m5_идея')
    btn4 = types.InlineKeyboardButton('❓ Сложно сказать', callback_data='m5_сложно')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== СООБЩЕНИЕ 6 и 7 ====================
def message6_and_7(chat_id):
    # Сначала сообщение 6
    bot.send_message(chat_id, "Спасибо, я зафиксировал Вашу задачу.\nЧтобы мы могли корректно оценить \nвозможность работы и предложить\nрешение, передам информацию специалисту")
    
    # Потом сообщение 7
    text = "Как удобнее продолжить общение?"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('📞 Телефонный звонок', callback_data='m7_звонок')
    btn2 = types.InlineKeyboardButton('💬 Написать в Telegram', callback_data='m7_telegram')
    btn3 = types.InlineKeyboardButton('📧 Электронная почта', callback_data='m7_почта')
    btn4 = types.InlineKeyboardButton('❓ Пока без связи, хочу задать вопрос', callback_data='m7_вопрос')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== СООБЩЕНИЕ 7.1 ====================

def message7_1(chat_id):
    text = "Как удобнее продолжить общение?"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('📞 Телефонный звонок', callback_data='m71_звонок')
    btn2 = types.InlineKeyboardButton('💬 Написать в Telegram', callback_data='m71_telegram')
    btn3 = types.InlineKeyboardButton('📧 Электронная почта', callback_data='m71_почта')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== СООБЩЕНИЕ 8 (Запрос телефона) ====================

def message8(chat_id, user_id, from_feedback=False):
    if from_feedback:
        user_states[user_id] = 'waiting_phone_for_feedback'
    else:
        user_states[user_id] = 'waiting_phone'
    
    text = "Пожалуйста, оставьте свой номер телефона"
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_phone = types.KeyboardButton('📱 Отправить мой номер', request_contact=True)
    keyboard.add(btn_phone)
    
    bot.send_message(chat_id, text, reply_markup=keyboard)

# ==================== СООБЩЕНИЕ 9 (Благодарность) ====================

def message9(chat_id, user_id):
    if user_id in user_states:
        del user_states[user_id]
    
    text = "Спасибо, мы передали информацию специалисту.\nОбычно ответ занимает до 1-2 рабочих\nчасов"
    bot.send_message(chat_id, text, reply_markup=get_main_keyboard())

# ==================== СООБЩЕНИЕ 10 (Запрос email) ====================

def message10(chat_id, user_id, from_feedback=False):
    if from_feedback:
        user_states[user_id] = 'waiting_email_for_feedback'
    else:
        user_states[user_id] = 'waiting_email'
    
    text = "Укажите электронную почту"
    bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())

# ==================== СООБЩЕНИЕ 11 (Вопрос) ====================

@bot.message_handler(func=lambda m: m.text == "💬 Задать вопрос")
def message11_handler(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Логируем действие
    log_action(user_id, username, first_name, 'button_click', 'Задать вопрос')
    
    user_states[user_id] = 'waiting_question'
    
    text = "Конечно 🙂\nНапишите ваш вопрос - я передам его специалисту"
    bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardRemove())

def message11(chat_id, user_id):
    user_states[user_id] = 'waiting_question'
    text = "Конечно 🙂\nНапишите ваш вопрос - я передам его специалисту"
    bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())

# ==================== СООБЩЕНИЕ 24, 25, 26 (Обратная связь) ====================
@bot.message_handler(func=lambda m: m.text == "⭐️ Обратная связь")
def message24(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Логируем действие
    log_action(user_id, username, first_name, 'button_click', '⭐️ Обратная связь')
    
    user_states[user_id] = 'waiting_feedback'
    
    text = "Нам важно Ваше мнение\nНапишите сообщение = это может быть\nвопрос, комментарий или пожелание."
    bot.send_message(message.chat.id, text, reply_markup=types.ReplyKeyboardRemove())

def message25_and_26(chat_id):
    # Сообщение 25
    bot.send_message(chat_id, "Спасибо за сообщение!\nМы предадим его команде.")
    
    # Сообщение 26
    text = "Если вы хотите получить ответ, выберите\nудобный способ связи:"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton('📞 Телефон', callback_data='m26_телефон')
    btn2 = types.InlineKeyboardButton('💬 Telegram', callback_data='m26_telegram')
    btn3 = types.InlineKeyboardButton('📧 Email', callback_data='m26_email')
    btn4 = types.InlineKeyboardButton('🔕 Ответ не требуется', callback_data='m26_нет')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)

# ==================== СООБЩЕНИЕ 27 ====================

def message27(chat_id, user_id):
    if user_id in user_states:
        del user_states[user_id]
    
    text = "Спасибо!\nМы учтем Ваше сообщение. Если\nпотребуется, свяжемся с Вами выбранным способ."
    bot.send_message(chat_id, text, reply_markup=get_main_keyboard())

# ==================== ОБРАБОТКА КОНТАКТА (номер телефона) ====================

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    phone = message.contact.phone_number
    
    # Логируем действие
    log_action(user_id, username, first_name, 'phone_provided', phone)
    
    # Уведомляем админа
    notify_admin(
        "📱 ПОЛУЧЕН ТЕЛЕФОН",
        first_name,
        user_id,
        username,
        f"☎️ Телефон: {phone}\n\n✅ Контакт отправлен через кнопку"
    )
    
    # Сохраняем данные
    data = load_data()
    if user_id not in data:
        data[user_id] = {}
    
    data[user_id]['phone'] = phone
    data[user_id]['name'] = message.from_user.first_name
    data[user_id]['username'] = message.from_user.username
    save_data(data)
    
    # Проверяем, откуда пришел запрос
    if user_states.get(user_id) == 'waiting_phone_for_feedback':
        message27(message.chat.id, user_id)
    else:
        message9(message.chat.id, user_id)

# ==================== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ (состояния) ====================
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    state = user_states.get(user_id)
    
    # Ожидание телефона (текстовый ввод)
    if state == 'waiting_phone':
        phone = message.text
        
        # Логируем действие
        log_action(user_id, username, first_name, 'phone_provided', phone)
        
        # Уведомляем админа
        notify_admin(
            "📱 ПОЛУЧЕН ТЕЛЕФОН",
            first_name,
            user_id,
            username,
            f"☎️ Телефон: {phone}\n\n✍️ Написан текстом"
        )
        
        # Сохраняем данные
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        
        data[user_id]['phone'] = phone
        data[user_id]['name'] = message.from_user.first_name
        data[user_id]['username'] = message.from_user.username
        save_data(data)
        
        message9(message.chat.id, user_id)
    
    # Ожидание email
    elif state == 'waiting_email':
        email = message.text
        
        # Логируем действие
        log_action(user_id, username, first_name, 'email_provided', email)
        
        # Уведомляем админа
        notify_admin(
            "📧 ПОЛУЧЕН EMAIL",
            first_name,
            user_id,
            username,
            f"📧 Email: {email}"
        )
        
        # Сохраняем данные
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        
        data[user_id]['email'] = email
        data[user_id]['name'] = message.from_user.first_name
        data[user_id]['username'] = message.from_user.username
        save_data(data)
        
        message9(message.chat.id, user_id)
    
    # Ожидание вопроса
    elif state == 'waiting_question':
        question = message.text
        
        # Логируем действие
        log_action(user_id, username, first_name, 'question_asked', question)
        
        # Уведомляем админа
        question_preview = question if len(question) < 200 else question[:200] + "..."
        notify_admin(
            "❓ НОВЫЙ ВОПРОС",
            first_name,
            user_id,
            username,
            f"💬 Вопрос:\n{question_preview}"
        )
        
        # Сохраняем данные
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        
        data[user_id]['question'] = question
        data[user_id]['name'] = message.from_user.first_name
        data[user_id]['username'] = message.from_user.username
        save_data(data)
        
        message9(message.chat.id, user_id)
    
    # Ожидание обратной связи
    elif state == 'waiting_feedback':
        feedback = message.text
        
        # Логируем действие
        log_action(user_id, username, first_name, 'feedback_provided', feedback)
        
        # Уведомляем админа
        feedback_preview = feedback if len(feedback) < 200 else feedback[:200] + "..."
        notify_admin(
            "💬 ОБРАТНАЯ СВЯЗЬ",
            first_name,
            user_id,
            username,
            f"💭 Сообщение:\n{feedback_preview}"
        )
        
        # Сохраняем данные
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        
        data[user_id]['feedback'] = feedback
        data[user_id]['name'] = message.from_user.first_name
        data[user_id]['username'] = message.from_user.username
        save_data(data)
        
        # Переходим к сообщению 25 и 26
        user_states[user_id] = 'waiting_feedback_choice'
        message25_and_26(message.chat.id)
    
    # Ожидание телефона для обратной связи
    elif state == 'waiting_phone_for_feedback':
        phone = message.text
        
        # Логируем действие
        log_action(user_id, username, first_name, 'phone_for_feedback', phone)
        
        # Сохраняем данные
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
            data[user_id]['phone'] = phone
        save_data(data)
        
        message27(message.chat.id, user_id)
    
    # Ожидание email для обратной связи
    elif state == 'waiting_email_for_feedback':
        email = message.text
        
        # Логируем действие
        log_action(user_id, username, first_name, 'email_for_feedback', email)
        
        # Сохраняем данные
        data = load_data()
        if user_id not in data:
            data[user_id] = {}
        
        data[user_id]['email'] = email
        save_data(data)
        
        message27(message.chat.id, user_id)

# ==================== ОБРАБОТКА INLINE-КНОПОК ====================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = str(call.from_user.id)
    username = call.from_user.username
    first_name = call.from_user.first_name
    
    # Логируем действие
    log_action(user_id, username, first_name, 'inline_button_click', call.data)
    
    bot.answer_callback_query(call.id)
    
    # Уведомляем о начале оформления заявки
    if call.data.startswith('m2_'):
        object_type = call.data.replace('m2_', '')
        notify_admin(
            "📝 НАЧАЛО ОФОРМЛЕНИЯ ЗАЯВКИ",
            first_name,
            user_id,
            username,
            f"🏗 Тип объекта: {object_type}\n\n📋 Пользователь начал оформлять заявку"
        )
    
    # Сообщение 2 → Сообщение 3
    if call.data.startswith('m2_'):
        message3(chat_id)
    
    # Сообщение 3 → Сообщение 4 или 5 или 7.1
    elif call.data == 'm3_изменение':
        message4(chat_id)
    elif call.data == 'm3_ремонт':
        message5(chat_id)
    elif call.data == 'm3_консультация':
        message7_1(chat_id)
    
    # Сообщение 4 → Сообщение 5
    elif call.data.startswith('m4_'):
        message5(chat_id)
    
    # Сообщение 5 → Сообщение 6+7
    elif call.data.startswith('m5_'):
        message6_and_7(chat_id)
    
    # Сообщение 7 → Сообщение 8, 9, 10 или 11
    elif call.data == 'm7_звонок':
        message8(chat_id, user_id)
    elif call.data == 'm7_telegram':
        message9(chat_id, user_id)
    elif call.data == 'm7_почта':
        message10(chat_id, user_id)
    elif call.data == 'm7_вопрос':
        message11(chat_id, user_id)
    
    # Сообщение 7.1 → Сообщение 8, 9 или 10
    elif call.data == 'm71_звонок':
        message8(chat_id, user_id)
    elif call.data == 'm71_telegram':
        message9(chat_id, user_id)
    elif call.data == 'm71_почта':
        message10(chat_id, user_id)
    
    # Сообщение 26 → Сообщение 8, 10 или 27
    elif call.data == 'm26_телефон':
        message8(chat_id, user_id, from_feedback=True)
    elif call.data == 'm26_telegram':
        message27(chat_id, user_id)
    elif call.data == 'm26_email':
        message10(chat_id, user_id, from_feedback=True)
    elif call.data == 'm26_нет':
        message27(chat_id, user_id)

# Запуск бота
if __name__ == '__main__':
    print("🤖 Основной бот запущен...")
    print(f"📢 Уведомления отправляются админу ID: {ADMIN_ID}")
    bot.remove_webhook()
    bot.infinity_polling()

