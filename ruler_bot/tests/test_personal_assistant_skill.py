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

from personal_assistant_skills.weather_skill import WeatherSkill
from personal_assistant_skills.alarm_setter_skill import AlarmSkill

# from persons_skill.persons_skill import PersonsSkill
from components.agent import AgentSkillEmulator


class WeatherBotTest(unittest.TestCase):

    # TODO make test where Slot (city) has default value
    # TODO make test where Slot (city) has default value and requires confirmation on silent value
    def setUp(self):
        self.agent = AgentSkillEmulator([WeatherSkill])
        self.test_phrase = "Weather Forecast in"

        import random
        salt = random.randint(0, 10e6)
        self.user_id = f"perpperonipizza_{salt}"

    def test_weather_no_prehist(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет?", "В москве", "ЗАВТРА"]
        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)

        self.assertIn(self.test_phrase, userdialog[5].text)


    def test_weather_prehistory_city(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет В МОСКВЕ?", "ЗАВТРА"]
        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)

        self.assertIn(self.test_phrase, userdialog[3].text)

    def test_weather_prehistory_date(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)

        self.assertEqual(userdialog[1].text, "В каком городе?")

        self.assertIn(self.test_phrase, userdialog[3].text)

    def test_weather_prehistory_date_and_city(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА в Москве?"]
        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)

        self.assertIn(self.test_phrase, userdialog[1].text)


class AlarmSetterBot(unittest.TestCase):
    def setUp(self):
        self.agent = AgentSkillEmulator([AlarmSkill])
        import random
        salt = random.randint(0, 10e6)
        self.user_id = f"perpperonipizza_{salt}"

        # actually setting the alarm phrase:
        self.test_phrase = "Я устанавливаю будильник на"

    def test_weather_active_questioning_date(self):
        # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
        user_messages_sequence = ["Приветик, Роботишка", "УСТАНОВИ БУДИЛЬНИК", "Чак Норрис бы не задавал такие вопросы", "ЗАВТРА", "ДА"]
        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)
        self.assertIn(self.test_phrase, userdialog[7].text)

    def test_weather_prehistory_date(self):
        # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
        user_messages_sequence = ["Приветик, Роботишка", "УСТАНОВИ БУДИЛЬНИК на завтра 16:00", "Чак Норрис бы не задавал такие вопросы", "ЗАВТРА", "ДА"]
        userdialog = self.agent.conjugate_autouser_with_agent(user_messages_sequence, self.user_id)
        self.assertIn(self.test_phrase, userdialog[3].text)


if __name__ == "__main__":
    unittest.main()
