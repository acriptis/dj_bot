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

# from scripts.bank_consulter import conjugate_agent_with_autouser
from introduction_skill.introduction_skill import IntroductionSkill

from root_skill.root_skill import RootSkill

# # ok
# class TestSilentAgent(unittest.TestCase):
#    def setUp(self):
#        self.agent = AgentSkillEmulator([])
#        self.user_id = "perpperonipizza"
#
#    def test_simple_reaction(self):
#        user_messages_sequence = ["ЗНАКОМСТВО, Приветик, Роботишка", "Чак Норрис бы не задавал такие вопросы"]
#        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)
#
#        self.assertIn("ЗНАКОМСТВО, Приветик, Роботишка", userdialog[0].text)
#        self.assertIn(self.agent.dontknowphrase, userdialog[1].text)
#        self.assertIn("Чак Норрис бы не задавал такие вопросы", userdialog[2].text)
#        self.assertIn(self.agent.dontknowphrase, userdialog[3].text)
#

# # ok
# class RulerAgentSkillLoopTest(unittest.TestCase):
#     """
#     Set up basic skill which reacts with standard reaction
#     """
#     def setUp(self):
#         self.agent = AgentSkillEmulator([IntroductionSkill, RootSkill])
#         import random
#         salt = random.randint(0, 10e6)
#         self.user_id = f"perpperonipizza_{salt}"
#
#     def test_simple_reaction(self):
#         user_messages_sequence = ["ЗНАКОМСТВО, Приветик, Роботишка",
#                                   "Чак Норрис бы не задавал такие вопросы", "Что дальше?", "Зови меня Валерой",
#                                   "Книги, викинги, динозавры и керлинг", "И что мне посоветуешь?"]
#         self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)


class IntroductionWithRestartTest(unittest.TestCase):
    """
    Set up basic skill which reacts with standard reaction
    """
    def setUp(self):
        self.agent = AgentSkillEmulator([RootSkill, IntroductionSkill])
        import random
        salt = random.randint(0, 10e6)
        self.user_id = f"perpperonipizza_{salt}"

    def test_simple_reaction(self):
        user_messages_sequence = ["ЗНАКОМСТВО, Приветик, Роботишка",
                                  "Чак Норрис бы не задавал такие вопросы", "Что дальше?", "Зови меня Валерой",
                                  "Книги, викинги, динозавры и керлинг", "/start", "ЗНАКОМСТВО, Приветик, Роботишка",
                                  "Зови меня Иванушкой", "я люблю гитару, керлинг и книги", "давай жги еще"
                                  ]
        self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)


#
# class RestrictedUsernameSlotTest(unittest.TestCase):
#     """
#     Test username slot with restrictive patterns
#     """
#     def setUp(self):
#         slots_factory = SlotsFactory()
#
#         self.username_slot = slots_factory.produce_username_text_slot(
#             'name_slot', "Как тебя зовут?", )
#
#     def test_pattern_receptor(self):
#         resp = self.username_slot.recept("Меня зовут Вася")
#         print(resp)
#         self.assertIn('value', resp)
#
#         resp = self.username_slot.recept("Чак норрис бы итак не сказал")
#
#         self.assertFalse(resp)

if __name__ == "__main__":
    unittest.main()