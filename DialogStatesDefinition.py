from DialogClasses import *
from Sqlighter import SQLighter
import universal_reply
import config
import utilities

wait_usr_interaction = State(name='WAIT_USR_INTERACTION',
                             triggers_out={'MAIN_MENU': {'phrases': ['/start'], 'content_type': 'text'}},
                             welcome_msg='')
# ----------------------------------------------------------------------------

main_menu = State(name='MAIN_MENU',
                  triggers_out={'PASS_HW_NUM_SELECT': {'phrases': ['Сдать дз'], 'content_type': 'text'},
                                'ASK_QUESTION_START': {'phrases': ['Задать вопрос к семинару'], 'content_type': 'text'},
                                'GET_MARK': {'phrases': ['Узнать оценки за дз'], 'content_type': 'text'},
                                'CHECK_HW_NUM_SELECT': {'phrases': ['Проверить дз'], 'content_type': 'text'},
                                'ADMIN_MENU': {'phrases': [universal_reply.ADMIN_KEY_PHRASE], 'content_type': 'text'}},
                  hidden_states=['ADMIN_MENU'],
                  welcome_msg='Выберите доступное действие, пожалуйста')

# ----------------------------------------------------------------------------

ask_question_start = State(name='ASK_QUESTION_START',
                           triggers_out={'MAIN_MENU': {'phrases': ['Назад'], 'content_type': 'text'},
                                         'SAVE_QUESTION': {'phrases': [], 'content_type': 'text'}},
                           welcome_msg='Сформулируйте вопрос к семинаристу и отправьте его одним сообщением.')


# ----------------------------------------------------------------------------

def save_question_handler(bot, message):
    sqlighter = SQLighter(config.bd_name)
    sqlighter.write_question(message.chat.username, message.text)


save_question = State(name='SAVE_QUESTION',
                      triggers_out={'MAIN_MENU': {'phrases': ['Назад'], 'content_type': 'text'},
                                    'SAVE_QUESTION': {'phrases': [], 'content_type': 'text'}},
                      handler_welcome=save_question_handler,
                      welcome_msg='Спасибо за вопрос. Хорошего дня 🐯 :)\n'
                                  'Если желаете задать еще вопрос, напишите его сразу следующим сообщением.'
                                  'Если у вас нет такого желания, воспользуйтесь кнопкой "Назад".')

# ----------------------------------------------------------------------------

pass_hw_num_selection = State(name='PASS_HW_NUM_SELECT',
                              row_width=2,
                              triggers_out={'PASS_HW_CHOSEN_NUM': {'phrases': config.hw_possible_to_pass,
                                                                   'content_type': 'text'},
                                            'MAIN_MENU': {'phrases': ['Назад'], 'content_type': 'text'}},
                              welcome_msg='Пожалуйста, выберите номер задания.')


# ----------------------------------------------------------------------------

def make_fake_db_record(bot, message):
    sqldb = SQLighter(config.bd_name)
    sqldb.make_fake_db_record(message.chat.username, message.text)


pass_hw_chosen_num = State(name='PASS_HW_CHOSEN_NUM',
                           triggers_out={'PASS_HW_UPLOAD': {'phrases': [], 'content_type': 'document'},
                                         'PASS_HW_NUM_SELECT': {'phrases': ['Назад'], 'content_type': 'text'}},
                           handler_welcome=make_fake_db_record,
                           welcome_msg='Пришлите файл **(один архив или один Jupyter notebook)** весом не более 20 Мб.')


# ----------------------------------------------------------------------------

class HwUploadState(State):
    def welcome_handler(self, bot, message):
        username = message.chat.username
        if not message.document.file_name.endswith(config.available_hw_resolutions):
            tmp_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tmp_markup.add(types.KeyboardButton('Меню'))
            bot.send_message(message.chat.id, "🚫 {}, очень жаль но файлик не сдается в нашу систему...\n"
                                              "Возможны следующие расширения файлов: {}.\n"
                                              "Напоминаю, что дз сдается в виде одного файла архива или одного Jupyter ноутбука."
                             .format(username.title(), str(config.available_hw_resolutions)), reply_markup=tmp_markup)
        else:
            sqldb = SQLighter(config.bd_name)
            hw_num = sqldb.upd_homework(user_id=username, file_id=message.document.file_id)
            bot.send_message(message.chat.id,
                             'Уважаемый *{}*, ваш файлик был заботливо сохранен как задание {} 🐾\n'
                             .format(username.title(), hw_num),
                             reply_markup=self.reply_markup, parse_mode='Markdown')

    def out_handler(self, bot, message):
        for state_name, attribs in self.triggers_out.items():
            if message.content_type == 'document':
                return self.welcome_handler(bot, message)

            elif (message.content_type == 'text') and (message.text in attribs['phrases']):
                return state_name
        return self.default_out_handler(bot, message)


pass_hw_upload = HwUploadState(name='PASS_HW_UPLOAD',
                               triggers_out={
                                   'PASS_HW_NUM_SELECT': {'phrases': ['Сдать еще одно дз'], 'content_type': 'text'},
                                   'MAIN_MENU': {'phrases': ['Меню'], 'content_type': 'text'}})


# ----------------------------------------------------------------------------

def show_marks_table(bot, message):
    pass


get_mark = State(name='GET_MARK',
                 triggers_out={'MAIN_MENU': {'phrases': ['Назад'], 'content_type': 'text'}},
                 handler_welcome=show_marks_table,
                 welcome_msg='Такие дела)')

# ----------------------------------------------------------------------------

check_hw_num_selection = State(name='CHECK_HW_NUM_SELECT',
                               triggers_out={'CHECK_HW_SEND': {'phrases': config.hw_possible_to_check,
                                                               'content_type': 'text'},
                                             'MAIN_MENU': {'phrases': ['Назад'], 'content_type': 'text'}},
                               welcome_msg='Выберите номер задания для проверки',
                               row_width=2)


# ----------------------------------------------------------------------------

def choose_file_and_send(bot, message):
    sqldb = SQLighter(config.bd_name)
    file_ids = sqldb.get_file_ids(hw_num=message.text, number_of_files=3)
    print(file_ids)


check_hw_send = State(name='CHECK_HW_SEND',
                      triggers_out={'CHECK_HW_SAVE_MARK': {'phrases': config.marks, 'content_type': 'text'}},
                      handler_welcome=choose_file_and_send,
                      row_width=3,
                      welcome_msg="Пожалуйста, оцените работу.")


# ----------------------------------------------------------------------------

def save_mark(bot, message):
    pass


check_hw_save_mark = State(name='CHECK_HW_SAVE_MARK',
                           triggers_out={'CHECK_HW_NUM_SELECT': {'phrases': ['Проверить еще одну работу'],
                                                                 'content_type': 'text'},
                                         'MAIN_MENU': {'phrases': ['Меню'],
                                                       'content_type': 'text'}},
                           welcome_msg='Спасибо за проверенную работу:)',
                           handler_welcome=save_mark)

# ----------------------------------------------------------------------------

admin_menu = State(name='ADMIN_MENU',
                   triggers_out={
                       'KNOW_NEW_QUESTIONS': {'phrases': ['Узнать вопросы к семинару'], 'content_type': 'text'},
                       'SEE_HW_STAT': {'phrases': ['Узнать статистику сдачи домашек'], 'content_type': 'text'},
                       'MAIN_MENU': {'phrases': ['Главное меню'], 'content_type': 'text'}},
                   welcome_msg='Добро пожаловать, о Великий Одмен!')


# ----------------------------------------------------------------------------

def get_questions(bot, message):
    pass


know_new_questions = State(name='KNOW_NEW_QUESTIONS',
                           triggers_out={'ADMIN_MENU': {'phrases': ['Назад в админку'], 'content_type': 'text'}},
                           handler_welcome=get_questions,
                           welcome_msg='Это все новые вопросы')


# ----------------------------------------------------------------------------

def get_hw_stat(bot, message):
    pass


see_hw_stat = State(name='SEE_HW_STAT',
                    triggers_out={'ADMIN_MENU': {'phrases': ['Назад в админку'], 'content_type': 'text'}},
                    handler_welcome=get_hw_stat,
                    welcome_msg='Это все домашки')
