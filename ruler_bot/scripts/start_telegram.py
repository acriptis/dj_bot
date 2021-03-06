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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
import django
django.setup()
# #####################################################

# from bank_consulter_skill.bank_consulter_skill import BankConsulterSkill
from components.agent import AgentSkillEmulator
from introduction_skill.introduction_skill import IntroductionSkill
from translator_skill.translator_skill import TranslatorSkill
from root_skill.root_skill import RootSkill
# from personal_assistant_skills.weather_skill import WeatherSkill
# from personal_assistant_skills.alarm_setter_skill import AlarmSkill


if __name__ == '__main__':
    """
    Fast bootstrapped script to make telegram bridge between Agent and Telegram
    You need to export environmental variable TG_BOT_TOKEN with your Telegram token before start
    """

    personal_agents = {}

    def init_agent():
        return AgentSkillEmulator([RootSkill, TranslatorSkill, IntroductionSkill])

    def start(bot, update):
        chat_id = update.message.chat_id
        personal_agents[chat_id] = init_agent()
        bot.send_message(chat_id=chat_id, text='Добрый день, человек. В чём ваша проблема?')

    def on_telegram_update(bot, update):
        """
        Callback called when telegram updater receives message
        Args:
            bot:
            update:

        Returns:

        """

        chat_id = update.message.chat_id
        user_msg = update.message.text
        print('{} >>> {}'.format(chat_id, user_msg))
        if chat_id not in personal_agents:
            personal_agents[chat_id] = init_agent()

        agent = personal_agents[chat_id]

        bot_resp_state = agent(user_msg, chat_id)
        print(bot_resp_state)
        #
        # for each_resp in bot_resp:
        text_resp = bot_resp_state['text']
        print('{} <<< {}'.format(chat_id, text_resp))
        bot.send_message(chat_id=chat_id, text=text_resp)


    updater = Updater(token=os.environ['TG_BOT_TOKEN'])
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    msg_handler = MessageHandler(Filters.text, on_telegram_update)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(msg_handler)

    updater.start_polling()
    updater.idle()
