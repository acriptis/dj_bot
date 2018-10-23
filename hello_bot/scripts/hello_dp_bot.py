
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
# #####################################################
from components.skills.base_skill import MonopolySkill
from components.matchers.matchers import RegExpMatcher

from components.matchers.matchers import TrainigPhrasesMatcher, PhraseGroupsMatcherController
from interactions.models import UserInteraction, SendTextOperation

class InformationTree():
    pass

class AbstractUserFrameInteraction():
    states = [
        "OFF",
        "ON",
    ]
    def __call__(self, *args, **kwargs):
        # activation
        pass

class FIOReceptor(RegExpMatcher):
    def __init__(self):

        self.template = "My name is .*"
        super().__init__(self.template)

    def check_match(self, text):
        match = re.search(self.template, text)
        if match:
            # load matched variables into instant memory
            # TODO
            return True
        else:
            return False


# class FIOExtractorInteraction(AbstractFrameInteraction):
#     question = "What is your fullname?"
#     variable = "FIO"
#     receptor = FIOReceptor

import typing
from typing import List
#
# class CustomAgent(Agent):
#     def __init__(self, skills: List[Component], skills_selector=None, skills_filter=None, *args, **kwargs):
#         pass
#
#     def percept(self, utterance):
#         """
#         Custom entry point for messages
#         :param utterance:
#         :return:
#         """
#         pass


class UserInfoModel():
    pass

class WIYNQAInteraction():
    """
    Interaction with what is your name capturing
    """
    def __init__(self):
        pass

    def quest(self):
        return "What is your name, dude?"

class WIYNDialogScenario():
    """
    Structure of Dialog Scenario for what is your name retrieval

    Bot which requests

    """

    def __init__(self):
        self.dialog_scenario_graph_spec = {
            "interactions": [
                {
                    'name': 'greeting',
                    'exit_gates': ["greeting_complete"]
                },
                {
                    'name': 'name_retriever',
                    'exit_gates': ['name_retriever.completed_gate', 'name_retriever.exception_gate']
                },
                {
                    'name': "bye",
                    'exit_gates': ['bye_gate']
                }
            ],
            'routes': [
                {
                    'name': 'greeting_then_retrieve_name',
                    'from_gate': "greeting_complete",
                    'to_interaction': 'name_retriever',
                },
                {
                    'name': 'name_retieved_bye',
                    'from_gate': 'name_retriever.completed_gate',
                    'to_interaction': 'bye'

                },
                {
                    'name': 'name_not_retieved_bye',
                    'from_gate': 'name_retriever.completed_gate',
                    'to_interaction': 'bye'
                }
            ]
        }
        # load into objects hierarchy
        # put global receptors to registry
        pass

class PersonalAgent(Agent):
    """
    In contrast to basic agent this model keeps user representation
    """
    def __init__(self):
        self.users_db = {}
        self.scenario_graph = WIYNDialogScenario()
        self.user_model = UserInfoModel()

    def percept(self, utterance):
        """
        given particular message from particular user routes it to UserMemory
        :param user:
        :param utterance:
        :return:
        """

        # 1. get state of dialog
        # 2. find active frame?

        # 2. find perceptors from registry?

        return "kek"



class InformationController():
    pass

class Frame():
    pass

class Question():
    pass

class Questor():
    """
    Specifies how to ask slot and activates answer receptor for listening the answer
    """
    pass

class QuestionResponseInteraction():
    def __init__(self, ic, question, var_name):
        self.ic = ic
        self.question = question


    def activate_interaction_process(self):
        pass


class SlotSpec():
    def __init__(self, name, validator, extractor):
        self.name=name
        self.validator=validator
        self.extractor=extractor



#
# title_slot = Slot(name='reminder title',
#                   code_name="reminder_title",
#                   datatype=str,
#                   if_needed=Questor('What is the title of reminder?'),
#                   if_added=None
#                   )
# time_slot = Slot()
# date_slot = Slot()
# reminder_frame=Frame(
#     title="Reminder Frame",
#     slots=[]
# )

class MultiChoiceMatcher():
    def __init__(self, choices):
        pass

class CoffeTeaInteraction():
    def __init__(self):

        pass

class CoffeTeaInteractionProcess():
    def __init__(self):
        pass
    pass

# def SendTextInteraction():

def test_fullname_questioning():
    user_events = ["Hello", "My name is Jonh Doe"]
    pa = PersonalAgent()
    # reactions = []
    chat_log = []
    for each_user_message in user_events:
        chat_log.append(each_user_message)
        reaction = pa.percept(each_user_message)
        chat_log.append(reaction)

    print(chat_log)

def phrase_matcher_hand_test():
    hi = TrainigPhrasesMatcher(training_phrases=["Hello", "Kek", "Hi"])
    bye = TrainigPhrasesMatcher(training_phrases=["Bye", "Lol", "Exit"])
    disjoint_matchers = [hi, bye]
    pgmc = PhraseGroupsMatcherController(disjoint_matchers)

    # ivanov_ivan_receptor = TrainigPhrasesMatcher(training_phrases=["Ivanov Ivan"])
    print("Kek")
    print(pgmc("Kek"))
    print("Bye")
    print(pgmc("Bye"))
    print("jasdhjsdh")
    print(pgmc("jasdhjsdh"))

    print("Hi Kek, Lol, ki")
    print(pgmc("Hi Kek, Lol, ki"))
    print("***********************")

def main():

    agent = Agent(
        skills=[
            # PatternMatchingSkill(responses=['Hello world!'], patterns=["hi", "hello", "good day"]),
            MonopolySkill()
        ],
        skills_selector=HighestConfidenceSelector())
    res = agent(["Hi", "Fuck"])
    print("res")
    print(res)
    import ipdb;
    ipdb.set_trace()
    ui = UserInteraction.activate(interaction=SendTextOperation(text="kuku, vatrushki!"))

    print(ui)

    # humans[chat_id] = Dialog(pipe, RuleBasedSberdemoNLU(), RuleBasedSberdemoPolicy())
    # bot.send_message(chat_id=chat_id, text='Добрый день, человек. В чём ваша проблема?')
    #
    # import sys
    # for line in sys.stdin:
    #     print(agent([line]), flush=True)


# TODO make outputs linking class


if __name__=="__main__":
    # test_fullname_questioning()
    phrase_matcher_hand_test()
    main()
    print("Fin.")