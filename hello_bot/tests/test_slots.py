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


from components.slots.slots_factory import SlotsFactory

class TestSlotConstruction(unittest.TestCase):
    def setUp(self):
        self.slots_factory = SlotsFactory()

    def test_create_categorical_slot(self):
        slot_instance = self.slots_factory.produce_categorical_slot(
            name="CustomCategoricalSlot",
            questioner="Question for the slot?",
            categories_domain_specification={
                "moscow": ["МОСКВА", "МСК", "ДЕФОЛТ-СИТИ", "МОСКВЕ"],
                "bobruisk": ["БОБРУЙСК", "БОБ"]
            }
        )

        self.assertFalse(slot_instance.can_recept(text="Них"))
        self.assertTrue(slot_instance.can_recept(text="МОСКВА"))
        self.assertIn("moscow", slot_instance.recept(text="МСК"))

    def test_cat_slot_interests(self):
        slot_instance = self.slots_factory.produce_categorical_slot(
            name='interests_slot',
            questioner="What is your hobbies, interests?",
            categories_domain_specification={
                "MOVIES": ["Кино", "Фильм"],
                "MUSIC": ["Музык", "Гитар"],
                "SPORT": ["Спорт", "Кёрлинг",
                          "Шахмат"],
                "BOOKS": ["Книги", "Чита"]
            })

        self.assertTrue(slot_instance.can_recept(text="Я люблбю кино"))
        self.assertTrue(slot_instance.can_recept(text="Я играю в шахматы"))
        self.assertTrue(slot_instance.can_recept(text="я гитарист"))
        self.assertIn("BOOKS", slot_instance.recept(text="Я люблю читать труды Ивана Павлова про кёрлинг"))
        print(slot_instance.recept(text="Я люблю читать труды Ивана Павлова про кёрлинг"))

    def test_create_yes_no_slot(self):
        slot_instance = self.slots_factory.produce_yes_no_slot("CustomYesNoSlot", "Question for the slot?")

        self.assertFalse(slot_instance.can_recept(text="Них"))
        self.assertTrue(slot_instance.can_recept(text="Да уж"))
        self.assertIn("Yes", slot_instance.recept(text="Да уж"))

    def test_create_text_slot(self):
        slot_instance = self.slots_factory.produce_free_text_slot(
            name="CustomTextSlot",
            questioner="Question for the slot?"
        )

        self.assertFalse(slot_instance.can_recept(text=""))
        self.assertTrue(slot_instance.can_recept(text="Них"))
        self.assertTrue(slot_instance.can_recept(text="МОСКВА"))


if __name__ == "__main__":
    unittest.main()