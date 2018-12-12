from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters
################# Universal Import ###################################################
import sys
import os



SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SELF_DIR)
PREROOT_DIR = os.path.dirname(ROOT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bank_bot.settings")
# #####################################################
import django
django.setup()

from bank_consulter_skill.bank_consulter_skill import BankConsulterSkill
from components.agent import AgentSkillInitializer
from root_skill.root_skill import RootSkill
from personal_assistant_skills.weather_skill import WeatherSkill
from personal_assistant_skills.alarm_setter_skill import AlarmSkill


if __name__ == '__main__':
    """
    Fast bootstrapped script to make telegram bridge between Agent and Telegram
    You need to export environmental variable TG_BOT_TOKEN with your Telegram token before start
    """

    humans = {}

    def init_agent():
        return AgentSkillInitializer([BankConsulterSkill, WeatherSkill, AlarmSkill, RootSkill])

    def start(bot, update):
        chat_id = update.message.chat_id
        humans[chat_id] = init_agent()
        bot.send_message(chat_id=chat_id, text='Добрый день, человек. В чём ваша проблема?')

    def user_client(bot, update):

        chat_id = update.message.chat_id
        user_msg = update.message.text
        print('{} >>> {}'.format(chat_id, user_msg))
        if chat_id not in humans:
            humans[chat_id] = init_agent()

        agent = humans[chat_id]

        bot_resp = agent(user_msg)
        one_resp = bot_resp[0]
        print('{} <<< {}'.format(chat_id, one_resp))

        bot.send_message(chat_id=chat_id, text=one_resp)


    updater = Updater(token=os.environ['TG_BOT_TOKEN'])
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(Filters.text, user_client)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(msg_handler)

    updater.start_polling()
    updater.idle()
