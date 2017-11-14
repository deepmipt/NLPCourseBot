import requests
import os
import config
from telebot import types


def make_right_keyboard(input_list, col_num, row_num, append_arr=None):
    tmp = [input_list[col_num * i: col_num * (i + 1)] for i in range(row_num)]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for row in tmp:
        markup.row(row)
    if append_arr is not None:
        markup.row(append_arr)
    return markup


def download_file(bot, file_id, folder_name, filename):
    file_info = bot.get_file(file_id)
    print(file_info.file_path)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.token, file_info.file_path),
                        stream=True)
    local_filename = os.path.join(folder_name, filename)
    with open(local_filename, 'wb') as f:
        for chunk in file.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
