# -*- coding: utf-8 -*-
import unittest
################# Universal Import ###################################################
import sys
import os


SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SELF_DIR)
PREROOT_DIR = os.path.dirname(ROOT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django

django.setup()

from components.slots.slots_factory import SlotsFactory
# from components.agent import AgentSkillInitializer
from components.agent import AgentSkillEmulator
from translator_skill.translator_skill import TranslatorSkill


class TestCurrencyConverterSkill(unittest.TestCase):
    """
    Set up basic skill which reacts with standard reaction
    """

    def setUp(self):
        self.agent = AgentSkillEmulator([TranslatorSkill])
        import random

        salt = random.randint(0, 10e6)
        self.user_id = f"perpperonipizza_{salt}"

    def test_simple_reaction(self):
        user_messages_sequence = ["Приветик, Роботишка",
                                  # "Как переводится слово mother",
                                  # "Что означает слово butter",
                                  # "Как по английски сказать вероятность",
                                  # "Переведи фразу besame mucho",
                                  # "что значит anticipatory",
                                  # "как переводится фраза salut mon amie",
                                  # "как будет по русски have",
                                  # "как по русски будет to",
                                  "перевод слова дом на английский",
                                  "перевод с английского слово часть"
        ]
        self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)

    def test_bunch_of_requests(self):
        test_lines = """Как по английски будет мама
Что значит слово pedaço
Что означает bessame mucho
Как по португальски сказать я еду домой
Переведи на испанский слово дочь
Переведи на японский воображение
Переведи созо с японского
Как перевести salut ca va с французского
как переводится anticipatory
что значит фраза Per aspera ad astra
как будет по русски have
как по русски будет to
перевод слова дом на английский
вайлдберриз перевод слова с английского
перевод на английский слово человек
перевод слова на английский lives
перевод слова done с английского на русский
перевод с английского на русский слово got
перевод с английского на русский слово could
перевод с английского на русский слово does
перевод с английского на русский слово doing
перевод с английского слова better
перевод с английского слово best
перевод с английского на русский слово went
перевод с английского на русский слово going
перевод с английского на русский слово better
перевод с английского на русский слово best
перевод с английского слова good
перевод с английского слово часть
перевод английского слова where
перевод английского слова live
перевод слова с английского going
перевод слова читать на английский
перевод слова история на английский
перевод слова мало на английский
перевод слова these с английского на русский
перевод слова год на английский
игра слов перевод на английский
перевод с английского на русский слово good
перевод английской песни русскими словами
вайлдберриз перевод слова с английского на русский
перевод слова книга на английском
как на английском пишется слово перевод
что в переводе означает английское слово хук
перевод слова 8 на английский
транскрипция и перевод слова дети английский
самые распространенные английские слова с переводом
произношение английских слов слушать онлайн с переводом
английские слова из 4 букв с переводом
500 английских слов с переводом и транскрипцией
часто употребляемые английские слова с переводом"""
        splitted_lines = test_lines.splitlines()
        self.agent.conjugate_autouser_with_agent(splitted_lines, self.user_id)


if __name__ == "__main__":
    unittest.main()

    #перевод слова на английский lives