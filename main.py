import telebot
from telebot import types

from config import TOKEN, FEEDBACK_CHAT_ID, EMPLOYEE_CHAT_ID
from utils import Parcer, Question, AnimalFactory, AnimalFinder, LineManager, BotLogger
from texts import ABOUT_URL, START_MSG, RES_MSG, EMPLOYEE_MESSAGE, FEEDBACK_MESSAGE, QUESTIONS
from animals import animals, element_dict, diet_dict, lifestyle_dict, society_dict


bot = telebot.TeleBot(TOKEN)
question = Question(QUESTIONS)
animal_factory = AnimalFactory(element_dict, diet_dict, lifestyle_dict, society_dict)
line_manager = LineManager()

@bot.message_handler(commands=['start'])
@BotLogger.log_performance
def handle_start(message):
    question.reset()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('О проекте', callback_data='about'))
    markup.add(types.InlineKeyboardButton('Начать викторину', callback_data='quiz'))
    bot.send_message(message.chat.id, START_MSG, reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
@BotLogger.log_performance
def callback_message(callback):
    if callback.data == 'about':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Назад', callback_data='back'))
        bot.send_message(callback.message.chat.id, Parcer.parse_about(ABOUT_URL), reply_markup=markup)
    if callback.data == 'back':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
    if callback.data == 'continue':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('О проекте', callback_data='about'))
        markup.add(types.InlineKeyboardButton('Начать викторину', callback_data='quiz'))
        bot.send_message(callback.message.chat.id, START_MSG, reply_markup=markup)
    if callback.data == 'call_employee':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Отмена', callback_data='cancel_feedback'))
        bot.send_message(callback.message.chat.id, EMPLOYEE_MESSAGE, reply_markup=markup)
        line_manager.open_line_employee()
    if callback.data == 'feedback':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Отмена', callback_data='cancel_feedback'))
        bot.send_message(callback.message.chat.id, FEEDBACK_MESSAGE, reply_markup=markup)
        line_manager.open_line_feedback()
    if callback.data == 'cancel_feedback':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        line_manager.cancel_line()
    if callback.data == 'quiz' or callback.data.isdigit():
        if callback.data.isdigit():
            animal_factory.set_сharact(callback.data)
        try:
            current_question = next(question)
        except StopIteration:
            user_animal = animal_factory.create_animal()
            try:
                animal_url = AnimalFinder.find_animal(user_animal, animals).url
            except AttributeError as e:
                animal_url = animals[0].url
                print(e)
            global animal_name
            animal_name = Parcer.parce_animal_name(animal_url)
            Parcer.parce_animal_image(animal_url)
            animal_factory.reset()
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('О проекте', callback_data='about')
            btn2 = types.InlineKeyboardButton('Подробнее о животном', url=animal_url)
            markup.row(btn1, btn2)
            btn3 = types.InlineKeyboardButton('Попробовать еще раз?', callback_data='quiz')
            btn4 = types.InlineKeyboardButton('Связаться с сотрудником', callback_data='call_employee')
            markup.row(btn3, btn4)
            btn5 = types.InlineKeyboardButton('Написать отзыв о работе бота', callback_data='feedback')
            markup.add(btn5)
            bot.send_photo(callback.message.chat.id, open('AnimalImage.jpg', 'rb'),
                           caption=f'Ваше тотемное животное: <b>{animal_name}\n</b>' + RES_MSG, reply_markup=markup, parse_mode='html')
        else:
            markup = types.InlineKeyboardMarkup()
            for i in range(1, len(current_question)):
                markup.add(types.InlineKeyboardButton(f'{current_question[i]}', callback_data=f'{i}'))
            bot.send_message(callback.message.chat.id, current_question[0], reply_markup=markup)

@bot.message_handler(content_types=['text'])
@BotLogger.log_performance
def feedback(message):
    question.reset()
    if line_manager.status == 1:
        bot.forward_message(FEEDBACK_CHAT_ID, message.chat.id, message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Продолжить', callback_data='continue'))
        bot.send_message(message.chat.id, 'Спасибо. Ваш отзыв будет передан разработчикам:-)', reply_markup=markup)
        line_manager.cancel_line()
    if line_manager.status == 2:
        bot.send_message(EMPLOYEE_CHAT_ID, f'Результат прохождения теста: {animal_name}')
        bot.forward_message(EMPLOYEE_CHAT_ID, message.chat.id, message.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Продолжить', callback_data='continue'))
        bot.send_message(message.chat.id, 'Спасибо. Ваш вопрос будет передан работнику зоопарка:-)', reply_markup=markup)
        line_manager.cancel_line()

bot.polling(none_stop=True)