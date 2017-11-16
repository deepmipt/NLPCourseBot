from typing import List, Dict, Callable
import universal_reply
from telebot import types
from collections import defaultdict
from Sqlighter import SQLighter


class State:
    def __init__(self, name: str,
                 triggers_out: Dict,
                 hidden_states: List = None,
                 welcome_msg: str = None,
                 row_width=1,
                 handler_welcome: Callable = None):
        """
        :param name: name of state object;
        :param triggers_out: dict like {state_out1_name:{'phrases':['some_string1', 'str2', etc],
                                                         'content_type':'text'}};
        :param hidden_states: list of state names that have to be reachable from this state
                              but they don't have to be shown on the keyboard;
        :param welcome_msg: what does the State have to say to usr after welcome_handler()
        :param handler_welcome: function that handle income message
        :param custom_markup: None or list of formatted buttons like this:
                                            [['top-left', 'top-right'],
                                            ['bottom-left', 'bottom-right']]

        """
        self.name = name
        self.hidden_states = hidden_states
        self.welcome_msg = welcome_msg
        self.triggers_out = triggers_out
        self.handler_welcome = handler_welcome
        self.row_width = row_width
        self.reply_markup = self.make_reply_markup()

    def make_reply_markup(self):

        markup = types.ReplyKeyboardMarkup(row_width=self.row_width, resize_keyboard=True)
        is_markup_filled = False
        tmp_buttons = []
        for state_name, attrib in self.triggers_out.items():
            hidden_flag = ((self.hidden_states is not None) and (state_name not in self.hidden_states)) \
                          or (self.hidden_states is None)
            if len(attrib['phrases']) > 0 and hidden_flag:
                for txt in attrib['phrases']:
                    tmp_buttons.append(types.KeyboardButton(txt))
                is_markup_filled = True

        markup.add(*tmp_buttons)
        if not is_markup_filled:
            markup = types.ReplyKeyboardRemove()
        return markup

    def welcome_handler(self, bot, message, sqldb: SQLighter):
        if self.handler_welcome is not None:
            self.handler_welcome(bot, message, sqldb)
        bot.send_message(message.chat.id, self.welcome_msg, reply_markup=self.reply_markup, parse_mode='Markdown')

    def default_out_handler(self, bot, message):
        if message.text == '/start':
            return 'MAIN_MENU'

        bot.send_message(message.chat.id, universal_reply.DEFAULT_ANS)
        return None

    def out_handler(self, bot, message, sqldb: SQLighter):
        """
        Default handler manage text messages and couldn't handle any photo/documents;
        It just apply special handler if it is not None;
        If message couldn't be handled None is returned;
        :param message:
        :param bot:
        :param sqldb:
        :return: name of the new state;

        """
        any_text_state = None
        for state_name, attribs in self.triggers_out.items():
            if message.content_type != 'text':
                if message.content_type == attribs['content_type']:
                    return state_name

            elif message.text in attribs['phrases']:
                return state_name

            # the case when any text message should route to state_name
            elif (len(attribs['phrases']) == 0) and (attribs['content_type'] == 'text'):
                any_text_state = state_name

        if any_text_state is not None:
            return any_text_state

        return self.default_out_handler(bot, message)


class DialogGraph:
    def __init__(self, bot, root_state: str, nodes: List[State], sqldb: SQLighter):
        """
        Instance of this class manages all the dialog flow;
        :param bot: telebot.TeleBot(token);
        :param nodes: list of instances of State class;
        :param root_state: name of the root of dialog states.
                            when new user appeared he/she has this state;
                            root state doesn't have "welcome" method;
        """
        self.bot = bot
        self.root_state = root_state
        self.nodes = self.make_nodes_dict(nodes)
        self.usr_states = defaultdict(dict)
        self.sqldb = sqldb

    def make_nodes_dict(self, nodes):
        return {state.name: state for state in nodes}

    def run(self, message):
        if message.chat.username is None:
            self.bot.send_message(message.chat.id, universal_reply.NO_USERNAME_WARNING)
            return

        if message.chat.id not in self.usr_states:
            self.usr_states[message.chat.id]['current_state'] = self.root_state

        curr_state_name = self.usr_states[message.chat.id]['current_state']
        new_state_name = self.nodes[curr_state_name].out_handler(self.bot, message, self.sqldb)

        if new_state_name is not None:
            self.usr_states[message.chat.id]['current_state'] = new_state_name
            self.nodes[new_state_name].welcome_handler(self.bot, message, self.sqldb)
