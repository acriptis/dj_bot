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


if __name__ == "__main__":
    unittest.main()