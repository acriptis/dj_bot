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

from components.skills.bank_consult_skill import BankConsulterAgentSkill


def main():
    import sys
    agent = BankConsulterAgentSkill()
    print("Write your message to dialogue bot:")
    for line in sys.stdin:
        print(">>>")
        print(agent(line), flush=True)
        print("^^^")
        agent.ic.userdialog.print_dialog()
        print("Write next message:")


def main2():
    # construct components hierarchy + domain data
    # hi = TrainigPhrasesMatcher(training_phrases=["Hello", "Kek", "Hi"])
    # bye = TrainigPhrasesMatcher(training_phrases=["Bye", "Lol", "Exit"])
    # disjoint_matchers = [hi, bye]
    # pgmc = PhraseGroupsMatcherController(disjoint_matchers)

    agent = BankConsulterAgentSkill()

    # user_messages_sequence = ["Приветик, Роботишка", "Рубли", "Пока"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ", "Пока"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "Пока"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!"]
    user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!",
                              "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов"]
    user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!",
                              "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов", "ДА", "Пока"]
    user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет", "ДА!",
                              "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ"]
    # ####################################################################################################
    # TODO make tests!
    # Test Cases #################################################################################################
    #
    # 1 check that text2.1 does not occur in dialog with messages:
    # ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ"]
    # 2 check that text2.1 occurs in dialog with messages:
    # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ"]
    # ####################################################################################################

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


if __name__=="__main__":

    main2()
    # main()
    print("Fin.")