import telebot
import datetime
import threading
from datetime import datetime, timedelta, timezone, tzinfo
from models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc

some_engine = create_engine('postgresql://root:1@postgres/board')
Session = sessionmaker(bind=some_engine)
session = Session()



print(datetime.now())
bot = telebot.TeleBot(token="6034043655:AAFmv4QfVZngsLizQ7bxEDloeuikM8-4qV8")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message): #Отправляем сообщение пользователю
    id = message.from_user.id
    registration_date = datetime.now() + timedelta(hours=7)
    user = User(id=id, registration_date=registration_date)
    session.add(user)
    session.commit()
    bot.send_message(message.chat.id, 'Привет! Я бот-напоминалка. Чтобы ознакомиться со всеми функциями бота нажмите /info')

@bot.message_handler(commands=['info'])
def reminder_message(message): # информация о боте
    bot.send_message(message.chat.id, 'Привет! Я бот-напоминание, помогу тебе не забыть свои дела и важные мероприятия.\n' 
                                       'Ниже указаны все функции бота и правила пользования:\n'
                                       '1. /reminder - добавить новое напоминание.\n'
                                       '2. /change_note - изменить напоминание. Отредактировать текст или время можно только с помощью этой функции! Если изменить сообщение в телеграме, изменения не сохранятся.\n'
                                       '3. /delete_note - удалить одно напоминание.\n'
                                       '4. /output_notes - вывод всех напоминаний.\n')

# Обработчик команды /reminder
@bot.message_handler(commands=['reminder'])
def reminder_message(message): # Запрашиваем у пользователя название напоминания и дату и время напоминания
    bot.send_message(message.chat.id, 'Введите название напоминания:')
    bot.register_next_step_handler(message, set_reminder_name)

# Функция, которую вызывает обработчик команды /reminder для установки названия напоминания
def set_reminder_name(message):
    text = message.text
    user_id = message.from_user.id
    board = Board(user_id=user_id, text=text)
    bot.send_message(message.chat.id, 'Введите дату и время, когда вы хотите получить напоминание в формате ГГГГ-ММ-ДД чч:мм:сс.')
    bot.register_next_step_handler(message, reminder_set, board)

# Функция, которую вызывает обработчик команды /reminder для установки напоминания
def reminder_set(message, board):
    try: # Преобразуем введенную пользователем дату и время в формат datetime
        date = datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
        board.date=date
        session.add(board)
        session.commit()
        now = datetime.now() + timedelta(hours=7)
        delta = date - now
# Если введенная пользователем дата и время уже прошли, выводим сообщение об ошибке
        if delta.total_seconds() <= 0:
            bot.send_message(message.chat.id, 'Вы ввели прошедшую дату, попробуйте еще раз.')
# Если пользователь ввел корректную дату и время, устанавливаем напоминание и запускаем таймер
        else:
            reminder_name = board.text
            reminder_time = board.date
            bot.send_message(message.chat.id, 'Напоминание "{}" установлено на {}.'.format(reminder_name, reminder_time))
            reminder_timer = threading.Timer(delta.total_seconds(), send_reminder, [message.chat.id, reminder_name])
            reminder_timer.start()
# Если пользователь ввел некорректную дату и время, выводим сообщение об ошибке
    except ValueError:
        bot.send_message(message.chat.id, 'Вы ввели неверный формат даты и времени, попробуйте еще раз.')

# Функция, которая отправляет напоминание пользователю
def send_reminder(chat_id, reminder_name):
    bot.send_message(chat_id, 'Время получить ваше напоминание "{}"!'.format(reminder_name))

@bot.message_handler(commands=['output_notes']) #Вывод всех напоминаний
def start_message(message): 
    bot.send_message(message.chat.id, 'Ваши напоминания:')
    msg = "".join(map(lambda b: 'id: ({}) {} {}\n'.format(b.id, b.date, b.text), 
                       session.query(Board).filter(Board.user_id == message.chat.id, 
                                                   Board.date > datetime.now() + timedelta(hours=7))
                            .order_by(desc(Board.date)).all()))
    
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['delete_note']) #удаление ненужных напоминаний
def start_message(message): 
    bot.send_message(message.chat.id, 'Выберите напоминание, которое нужно удалить по его id:')
    msg = "".join(map(lambda b: 'id: ({}) {} {}\n'.format(b.id, b.date, b.text), 
                       session.query(Board).filter(Board.user_id == message.chat.id, 
                                                   Board.date > datetime.now() + timedelta(hours=7))
                            .order_by(desc(Board.date)).all()))
    bot.send_message(message.chat.id, msg)
    bot.register_next_step_handler(message, message_input_step)

# Функция, которую вызывает обработчик команды /delete_note для удаления напоминания
def message_input_step(message):
    f = message.text
    i = session.query(Board).filter(Board.id == f).one()
    session.delete(i)
    session.commit()
    bot.send_message(message.chat.id, 'Напоминание было успешно удалено')

@bot.message_handler(commands=['change_note']) #Изменение заметок
def start_message(message): 
    bot.send_message(message.chat.id, 'Выберите напоминанение, которое нужно изменить по id:')
    msg = "".join(map(lambda b: 'id: ({}) {} {}\n'.format(b.id, b.date, b.text), 
                       session.query(Board).filter(Board.user_id == message.chat.id, 
                                                   Board.date > datetime.now() + timedelta(hours=7))
                            .order_by(desc(Board.date)).all()))
    bot.send_message(message.chat.id, msg)
    bot.register_next_step_handler(message, message_change)

def message_change(message):
    f = message.text
    bot.send_message(message.chat.id, 'Напишите, что нужно изменить (время или текст)')
    bot.register_next_step_handler(message, message_change_note, f)

def message_change_note(message, f):
    g = message.text
    t = ['время', 'Время']
    te = ['Текст', 'текст']

    if (g in t):
        bot.send_message(message.chat.id, 'Введите дату и время, когда вы хотите получить напоминание в формате ГГГГ-ММ-ДД чч:мм:сс.')
        bot.register_next_step_handler(message, new_time, f)
    elif (g in te):
        bot.send_message(message.chat.id, 'Введите название напоминания:')
        bot.register_next_step_handler(message, new_text, f)
    else:
        bot.send_message(message.chat.id, 'Вы неправильно ввели слово, попробуйте ещё раз')
        bot.register_next_step_handler(message, message_change_note, f)

#Функция для изменения времени в напоминании
def new_time(message, f):
    time = message.text
    i = session.query(Board).filter(Board.id == f).one()
    i.date = time
    session.add(i)
    session.commit()
    bot.send_message(message.chat.id, 'Напоминание успешно изменено')

#Функция для изменения текста в напоминании
def new_text(message, f):
    txt = message.text
    i = session.query(Board).filter(Board.id == f).one()
    i.text = txt
    session.add(i)
    session.commit()
    bot.send_message(message.chat.id, 'Напоминание успешно изменено')

# Обработчик любого сообщения от пользователя
@bot.message_handler(func=lambda message: True)
def handle_all_message(message):
    bot.send_message(message.chat.id, 'Я не понимаю, что вы говорите. Чтобы ознакомиться с информацией нажмите /info')

# Запускаем бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
    