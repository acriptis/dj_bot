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

from components.agent import AgentSkillEmulator

from ecommerce_skill.ecommerce_skill import ECommerceSkill



class TestECommerceSkill(unittest.TestCase):
    """
    Set up basic skill which reacts with standard reaction
    """

    def setUp(self):
        self.agent = AgentSkillEmulator([ECommerceSkill])
        import random

        salt = random.randint(0, 10e6)
        self.user_id = f"perpperonipizza_{salt}"

    # def test_pay_by_cash(self):
    #     user_messages_sequence = ["найди мне желтые туфельки",
    #                               "покажи второй товар",
    #                               "Добавь первую туфельку в корзину",
    #                               "Добавь розовую туфельку в корзину",
    #                               "покажи корзину",
    #                               "давай перейдем к покупке",
    #                               "Доставка курьером",
    #                               "Иванов Иван Иванович",
    #                               "911",
    #                               "г. Урюписнк, улица Сапогова, 3, 14",
    #                               "Оплата кешем",
    #                               "Спасибо братюня"
    #     ]
    #     userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)
    #     # self.assertIn("Well, hello!", userdialog[1].text)

    def test_pay_by_card(self):
        user_messages_sequence = ["найди мне желтые туфельки",
                                  "покажи второй товар",
                                  "Добавь первую туфельку в корзину",
                                  "Добавь розовую туфельку в корзину",
                                  "покажи корзину",
                                  "давай перейдем к покупке",
                                  "Доставка курьером",
                                  "Иванов Иван Иванович",
                                  "911",
                                  "г. Урюписнк, улица Сапогова, 3, 14",
                                  "Оплата картой",
                                  "445566778899",
                                  "321",
                                  "Ivanov Ivan",
                                  "123456",
                                  "Спасибо братюня"]
        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)
        # self.assertIn("Well, hello!", userdialog[1].text)

if __name__ == "__main__":
    unittest.main()

    #перевод слова на английский lives