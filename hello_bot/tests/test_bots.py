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
from persons_skill.persons_skill import PersonsSkill

# class BotContextSwitchTest(unittest.TestCase):
#     def setUp(self):
#         self.agent = AgentSkillInitializer([BankConsulterSkill, WeatherSkill, AlarmSkill])
#         # start bank consulting then ask about weather during specification of city slot ask to set alarm?
#
#     def test_cswitch1(self):
#         # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?",
#         #                           "РУБЛИ и БАКСЫ", "ДА", "ОПЕРАТОР", "ДА", "МСК", "ИП",
#         #                           "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
#         user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?",
#                                   "в МСК"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         # check non ruble currencies trigger non rub specific text:
#         # import ipdb; ipdb.set_trace()
#
#         self.assertIn("В каком городе?", userdialog[6])
#         # self.assertIn("Вавилова, 19", userdialog[39])
#
#     def test_double_cswitch(self):
#         """
#         Test fails if Prehistory receptor of DateTimeSlot alarm recepts by prehistory the text aimed for the WeatherDateTime slot
#         :return:
#         """
#         # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?",
#         #                           "РУБЛИ и БАКСЫ", "ДА", "ОПЕРАТОР", "ДА", "МСК", "ИП",
#         #                           "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
#         user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?", "УСТАНОВИ БУДИЛЬНИК",
#                                   "в МСК", "на 16:00 во вторник"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         # check non ruble currencies trigger non rub specific text:
#         # import ipdb; ipdb.set_trace()
#
#         self.assertIn("В каком городе?", userdialog[6])
#         # self.assertIn("Вавилова, 19", userdialog[39])
#
#     def test_double_cswitch2(self):
#         """
#         Test double context switch, from bank skill to weather skill, then to alarm skill
#         :return:
#         """
#         # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?",
#         #                           "РУБЛИ и БАКСЫ", "ДА", "ОПЕРАТОР", "ДА", "МСК", "ИП",
#         #                           "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
#         user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет в Москве, МСК?",
#                                   "УСТАНОВИ БУДИЛЬНИК",
#                                   "на 16:00 во вторник"]
#
#         # TODO fix a bug when dateparser splits phrase "на 16:00 во вторник" into two separate datetime objects
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         # check non ruble currencies trigger non rub specific text:
#         # import ipdb; ipdb.set_trace()
#
#         self.assertIn("Погода на какой день интересует вас?", userdialog[6])
#         self.assertIn("На какое время установить будильник?", userdialog[8])
#         # self.assertIn("Вавилова, 19", userdialog[39])
#
#     def test_double_cswitch3(self):
#         """
#         Test double context switch, from bank skill to weather skill, then to alarm skill
#         :return:
#         """
#         # user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет ЗАВТРА?",
#         #                           "РУБЛИ и БАКСЫ", "ДА", "ОПЕРАТОР", "ДА", "МСК", "ИП",
#         #                           "ДА, согласен с условиями пакетов", "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
#         user_messages_sequence = ["Приветик, Роботишка", "ОБЩАЯ, СЕКРЕТ", "А КАКАЯ ПОГОДА будет в Москве, МСК?",
#                                   "УСТАНОВИ БУДИЛЬНИК",
#                                   "вторник в 16:00"]
#
#         # TODO fix a bug when time of alarm is also grasped by DateTime slot of WeatherForecast
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         # check non ruble currencies trigger non rub specific text:
#         # import ipdb; ipdb.set_trace()
#
#         self.assertIn("Погода на какой день интересует вас?", userdialog[6])
#         self.assertIn("На какое время установить будильник?", userdialog[8])
#         self.assertIn("В какой валюте?", userdialog[4])
#         self.assertIn("В какой валюте?", userdialog[12])
#         # self.assertIn("Вавилова, 19", userdialog[39])

#
# class BankScenarioBotTest(unittest.TestCase):
#
#     def setUp(self):
#         self.agent = AgentSkillInitializer([BankConsulterSkill])
#
#     def test_multicur(self):
#         user_messages_sequence = ["Приветик, Роботишка", "Куку", "ОБЩАЯ, СЕКРЕТ", "РУБЛИ и БАКСЫ", "ДА", "Оги-оги, Привет",
#                                   "ДА!", "ДА", "МСК", "ИП", "ДА, согласен с условиями пакетов",
#                                   "НЕТ", "ДА", "КЕК", "Ну ладно", "ДА", "Пока"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         # check non ruble currencies trigger non rub specific text:
#         self.assertIn("Текст 2.1", userdialog[8])
#         self.assertIn("Вавилова, 19", userdialog[39])
#
#
# class WeatherBotTest(unittest.TestCase):
#
#     # TODO make test where Slot (city) has default value
#     # TODO make test where Slot (city) has default value and requires confirmation on silent value
#     def setUp(self):
#         self.agent = AgentSkillInitializer([WeatherSkill])
#         self.test_phrase = "Weather Forecast in"
#
#     def test_weather_no_prehist(self):
#         user_messages_sequence = ["КАКАЯ ПОГОДА будет?", "В москве", "ЗАВТРА"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         self.assertIn(self.test_phrase, userdialog[5])
#
#
#     def test_weather_prehistory_city(self):
#         user_messages_sequence = ["КАКАЯ ПОГОДА будет В МОСКВЕ?", "ЗАВТРА"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         self.assertIn(self.test_phrase, userdialog[3])
#
#     def test_weather_prehistory_date(self):
#         user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#         self.assertEqual(userdialog[1], "В каком городе?")
#
#         self.assertIn(self.test_phrase, userdialog[3])
#
#     def test_weather_prehistory_date_and_city(self):
#         user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА в Москве?"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         self.assertIn(self.test_phrase, userdialog[1])
#
# class AlarmSetterBot(unittest.TestCase):
#     def setUp(self):
#         self.agent = AgentSkillInitializer([AlarmSkill])
#         # actually setting the alarm phrase:
#         self.test_phrase = "Я устанавливаю будильник на"
#
#     def test_weather_active_questioning_date(self):
#         # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
#         user_messages_sequence = ["Приветик, Роботишка", "УСТАНОВИ БУДИЛЬНИК", "Чак Норрис бы не задавал такие вопросы", "ЗАВТРА", "ДА"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#         self.assertIn(self.test_phrase, userdialog[6])
#
#     def test_weather_prehistory_date(self):
#         # user_messages_sequence = ["КАКАЯ ПОГОДА будет ЗАВТРА?", "МОСКВА"]
#         user_messages_sequence = ["Приветик, Роботишка", "УСТАНОВИ БУДИЛЬНИК на завтра 16:00", "Чак Норрис бы не задавал такие вопросы", "ЗАВТРА", "ДА"]
#         userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
#
#         # self.assertIn(self.test_phrase, userdialog[6])
#



class PersonsReceptorTest(unittest.TestCase):
    def setUp(self):
        self.agent = AgentSkillInitializer([PersonsSkill])

    def test_obama(self):
        print(":dsfs")
        # user_messages_sequence = ["I was playing hockey with Barack Obama", "Yes, of course I know him"]
        user_messages_sequence = ["Напомни завтра купить сырок маме Гали и раскажи прогноз погоды Василию Дементьевичу в Москве на 16 января", "Yes, of course I know him"]
        userdialog = conjugate_agent_with_autouser(self.agent, user_messages_sequence)
        import ipdb; ipdb.set_trace()

        self.assertIn("Do you know Barack Obama?", userdialog[1])


if __name__ == "__main__":
    unittest.main()