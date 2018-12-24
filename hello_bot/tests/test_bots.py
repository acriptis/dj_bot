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
from bank_consulter_skill.bank_consulter_skill import BankConsulterSkill
from components.agent import AgentSkillInitializer
from personal_assistant_skills.weather_skill import WeatherSkill
from personal_assistant_skills.alarm_setter_skill import AlarmSkill
from scripts.bank_consulter import conjugate_agent_with_autouser

class BotContextSwitchTest(unittest.TestCase):
    def setUp(self):
        self.agent = AgentSkillInitializer([BankConsulterSkill, WeatherSkill, AlarmSkill])
        # start bank consulting then ask about weather during specification of city slot ask to set alarm?

    def test_cswitch1(self):
        # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?",
        #                           "РУБЛИ и БАКСЫ", "ДА", "ОПЕРАТОР", "ДА", "МСК", "ИП",
        #                           "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
        user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?",
                                  "в МСК"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

        # check non ruble currencies trigger non rub specific text:
        # import ipdb; ipdb.set_trace()

        self.assertIn("В каком городе?", userdialog[6])
        # self.assertIn("Вавилова, 19", userdialog[39])


class BankScenarioBotTest(unittest.TestCase):

    def setUp(self):
        self.agent = AgentSkillInitializer([BankConsulterSkill])

    def test_multicur(self):
        user_messages_sequence = ["Приветик, Роботишка", "Куку", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет",
                                  "ДА!", "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов",
                                  "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

        # check non ruble currencies trigger non rub specific text:
        self.assertIn("Текст 2.1", userdialog[8])
        self.assertIn("Вавилова, 19", userdialog[39])


class WeatherBotTest(unittest.TestCase):

    # TODO make test where Slot (city) has default value
    # TODO make test where Slot (city) has default value and requires confirmation on silent value
    def setUp(self):
        self.agent = AgentSkillInitializer([WeatherSkill])
        self.test_phrase = "Weather Forecast in"

    def test_weather_no_prehist(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет?", "В москве", "ЗАВТРА"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

        self.assertIn(self.test_phrase, userdialog[5])


    def test_weather_prehistory_city(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет В МОСКВЕ?", "ЗАВТРА"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

        self.assertIn(self.test_phrase, userdialog[3])

    def test_weather_prehistory_date(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
        self.assertEqual(userdialog[1], "В каком городе?")

        self.assertIn(self.test_phrase, userdialog[3])

    def test_weather_prehistory_date_and_city(self):
        user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА в Москве?"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

        self.assertIn(self.test_phrase, userdialog[1])

class AlarmSetterBot(unittest.TestCase):
    def setUp(self):
        self.agent = AgentSkillInitializer([AlarmSkill])
        # actually setting the alarm phrase:
        self.test_phrase = "Я устанавливаю будильник на"

    def test_weather_active_questioning_date(self):
        # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
        user_messages_sequence = ["Приветик, Роботишка", "УСТАНОВИ БУДИЛЬНИК", "Чак Норрис бы не задавал такие вопросы", "ЗАВТРА", "ДА"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
        self.assertIn(self.test_phrase, userdialog[6])

    def test_weather_prehistory_date(self):
        # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
        user_messages_sequence = ["Приветик, Роботишка", "УСТАНОВИ БУДИЛЬНИК на завтра 16:00", "Чак Норрис бы не задавал такие вопросы", "ЗАВТРА", "ДА"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)

        # self.assertIn(self.test_phrase, userdialog[6])

if __name__ == "__main__":
    unittest.main()