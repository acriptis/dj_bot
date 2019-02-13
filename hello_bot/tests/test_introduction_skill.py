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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bank_bot.settings")
# #####################################################
import django
django.setup()

from components.agent import AgentSkillInitializer

from scripts.bank_consulter import conjugate_agent_with_autouser
from introduction_skill.introduction_skill import IntroductionSkill
from root_skill.root_skill import RootSkill

class IntroductionBotTest(unittest.TestCase):
    def setUp(self):
        self.agent = AgentSkillInitializer([IntroductionSkill, RootSkill])


    def test_basic(self):
        # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
        user_messages_sequence = ["ЗНАКОМСТВО, Приветик, Роботишка", "Чак Норрис бы не задавал такие вопросы",
                                  "СПОРТ, МУЗЫКА и КНИГИ", "Agenda", "Memory","КЕКЕ", "sddsfdsf"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

    # def test_basic2(self):
    #     # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
    #     user_messages_sequence = ["ЗНАКОМСТВО, Приветик, Роботишка",
    #                               "УСТАНОВИ БУДИЛЬНИК на завтра 16:00",
    #                               "Чак Норрис бы не задавал такие вопросы",
    #                               "СПОРТ, МУЗЫКА и КНИГИ", "КЕКЕ", "sddsfdsf"]
    #     userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

if __name__ == "__main__":
    unittest.main()