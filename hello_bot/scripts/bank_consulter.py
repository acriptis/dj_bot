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

from components.agent import AgentSkillInitializer
from bank_consulter_skill.bank_consulter_skill import BankConsulterSkill
from personal_assistant_skills.weather_skill import WeatherSkill
from personal_assistant_skills.alarm_setter_skill import AlarmSkill


def main(agent):
    import sys

    print("Write your message to dialogue bot:")
    for line in sys.stdin:
        print(">>>")
        print(agent(line), flush=True)
        print("^^^")
        agent.ic.userdialog.print_dialog()
        print("Write next message:")

def conjugate_agent_with_autouser(agent, user_messages_sequence):
    """

    :param agent:
    :param user_messages_sequence:
    :return: UserDialog?
    """
    for line in user_messages_sequence:
        print(">>>"*30)
        agent.ic.userdialog.print_dialog()
        print("New Message: %s" % line)
        print("VVV"*45)

        print(agent(line), flush=True)
        print("^^^"*30)
        # import ipdb; ipdb.set_trace()


    print("="*80)
    print("Final Dialog Content:")
    agent.ic.userdialog.print_dialog()
    return agent.ic.userdialog

def main_user_emulated_replies(agent):
    # construct components hierarchy + domain data
    # user_messages_sequence = ["Приветик, Роботишка", "Рубли", "Пока"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ", "Пока"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "Пока"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!"]
    user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!",
                              "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов"]
    user_messages_sequence = ["Приветик, Роботишка", "Привет", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!",
                              "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов", "ДА", "Вероятно, ДА", "ДА!","Пока"]

    user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?","РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!",
                              "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]

    user_messages_sequence = ["Приветик, Роботишка", "Уги", "общая, секрет", "А КАКАЯ ПОГОДА будет ЗАВТРА?", "Погода!",
                              "ДА"]

    # Test Operator switch within dialog
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?", "РУБЛИ и БАКСЫ",
    #                           "ДА", "ОПЕРАТОР",
    #                           "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно",
    #                           "ДА", "Пока"]

    # ########################################################################################################
    # FAILED TESTS
    # Тестовые сценарии
    # Падает:
    # user_messages_sequence = ["Приветик, Роботишка", "СЕКРЕТ", "РУБЛИ", "НЕТ"]
    # не знает что ответить:
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ", "БАКСЫ, РУБЛИ", "НЕТ", "ДА"]
    # user_messages_sequence = ["Приветик, Роботишка", "КАКАЯ ПОГОДА будет В МОСКВЕ?", "МОСКВА, БОБРУЙСК", "ЗАВТРА", "ДА"]
    # user_messages_sequence = ["Приветик, Роботишка", "УСТАНОВИ БУДИЛЬНИК", "МОСКВА, БОБРУЙСК", "ЗАВТРА", "ДА"]


    # ####################################################################################################
    # TODO make tests!
    # Test Cases #################################################################################################
    #
    # 1 check that text2.1 does not occur in dialog with messages:
    # ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ"]
    # 2 check that text2.1 occurs in dialog with messages:
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ"]
    # ####################################################################################################
    conjugate_agent_with_autouser(agent, user_messages_sequence)


if __name__=="__main__":

    # construct the agent:

    # agent = AgentSkillInitializer([BankConsulterSkill])
    # agent = AgentSkillInitializer([BankConsulterSkill, WeatherSkill])
    # agent = AgentSkillInitializer([WeatherSkill])
    # agent = AgentSkillInitializer([AlarmSkill])
    agent = AgentSkillInitializer([BankConsulterSkill, WeatherSkill, AlarmSkill])
    # main_user_emulated_replies(agent)
    main(agent)
    print("Fin.")