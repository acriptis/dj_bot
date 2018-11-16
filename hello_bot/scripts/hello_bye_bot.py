

from deeppavlov.skills.pattern_matching_skill import PatternMatchingSkill
from deeppavlov.core.agent import Agent, HighestConfidenceSelector
from deeppavlov.core.common.registry import register
from deeppavlov.core.common.log import get_logger
from deeppavlov.core.common.file import save_pickle, load_pickle
from deeppavlov.core.commands.utils import expand_path, make_all_dirs, is_file_exist
from deeppavlov.core.models.estimator import Component
from deeppavlov.metrics.bleu import bleu_advanced
from deeppavlov.core.models.component import Component
import re
import random
################# Universal Import ###################################################
import sys
import os
SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SELF_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bank_bot.settings")
# #####################################################
import django
from django.conf import settings
# from hello_bot import settings as my_app_settings

# settings.configure(DEBUG=True)
# settings.configure(my_app_settings)
django.setup()

from components.skills.base_skill import MonopolySkill, MonopolyAgentSkill
from components.matchers.matchers import RegExpMatcher

from components.matchers.matchers import TrainigPhrasesMatcher, PhraseGroupsMatcherController


def main2():
    import sys
    agent = MonopolyAgentSkill()
    print("Write your message to dialogue bot:")
    for line in sys.stdin:
        print(">>>")
        print(agent(line), flush=True)
        print("^^^")
        agent.ic.userdialog.print_dialog()
        print("Write next message:")


def main():
    # construct components hierarchy + domain data
    # hi = TrainigPhrasesMatcher(training_phrases=["Hello", "Kek", "Hi"])
    # bye = TrainigPhrasesMatcher(training_phrases=["Bye", "Lol", "Exit"])
    # disjoint_matchers = [hi, bye]
    # pgmc = PhraseGroupsMatcherController(disjoint_matchers)

    agent = MonopolyAgentSkill()

    print("*"*40)
    res = agent("Hi")

    print(res)
    print("*"*40)
    res = agent("Bye")
    print(res)
    print("*"*40)
    res = agent("Konichiua")
    print(res)
    
    print("agent.ic.userdialog")
    agent.ic.userdialog.print_dialog()
    # res = agent(["Hi", "Fuck"])
    # print("res")
    # print(res)
    # import ipdb;
    # ipdb.set_trace()
    # ui = UserInteraction.activate(interaction=SendTextOperation(text="kuku, vatrushki!"))

    # print(ui)

if __name__=="__main__":

    # main()
    main2()
    print("Fin.")