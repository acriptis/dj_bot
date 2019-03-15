# -*- coding: utf-8 -*-
import unittest
################# Universal Import ###################################################
import sys
import os

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SELF_DIR)))
PREROOT_DIR = os.path.dirname(ROOT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django

django.setup()
import pprint

from translator_skill.translator_intents_receptor.translator_perceptor.translate_intent_perceptor import \
    RegexpTranslatePerceptor


class TestCurrencyConverterSkill(unittest.TestCase):
    """
    Set up basic skill which reacts with standard reaction
    """

    def setUp(self):
        self.perceptor = RegexpTranslatePerceptor()

    def test_positives(self):
        receptor_out = self.perceptor("перевод на английский слово человек")
        self.assertEquals(receptor_out['phrase_to_translate'], "человек")
        self.assertEquals(receptor_out['target_language_code_candidates'], ["en"])

        receptor_out = self.perceptor("Переведи на испанский слово дочь")
        self.assertEquals(receptor_out['phrase_to_translate'], "дочь")
        self.assertEquals(receptor_out['target_language_code_candidates'], ["es"])

        receptor_out = self.perceptor("Что значит слово pedaço")
        self.assertEquals(receptor_out['phrase_to_translate'], "pedaço")
        self.assertIn("ru", receptor_out['target_language_code_candidates'])

        receptor_out = self.perceptor("Как на японский перевести pedaço")
        self.assertEquals(receptor_out['phrase_to_translate'], "pedaço")
        self.assertIn("ja", receptor_out['target_language_code_candidates'])
        self.assertEquals(receptor_out['target_language_code_candidates'], ["ja"])

        receptor_out = self.perceptor("Как по английски будет мама")
        self.assertEquals(receptor_out['phrase_to_translate'], "мама")
        self.assertIn("en", receptor_out['target_language_code_candidates'])

        receptor_out = self.perceptor("Что означает bessame mucho")
        self.assertEquals(receptor_out['phrase_to_translate'], "bessame mucho")
        self.assertIn("ru", receptor_out['target_language_code_candidates'])

        receptor_out = self.perceptor("Как по португальски сказать я еду домой")
        self.assertEquals(receptor_out['phrase_to_translate'], "я еду домой")
        self.assertIn("pt", receptor_out['target_language_code_candidates'])
        self.assertEquals(receptor_out['target_language_code_candidates'], ["pt"])

        receptor_out = self.perceptor("Переведи на японский воображение")
        self.assertEquals(receptor_out['phrase_to_translate'], "воображение")
        self.assertIn("ja", receptor_out['target_language_code_candidates'])
        self.assertEquals(receptor_out['target_language_code_candidates'], ["ja"])

        receptor_out = self.perceptor("Переведи созо с японского")
        self.assertEquals(receptor_out['phrase_to_translate'], "созо")
        self.assertIn("ja", receptor_out['target_language_code_candidates'])
        self.assertEquals(receptor_out['detected_phrase_to_translate_language'], "ru")
        self.assertEquals(receptor_out['language_entities'], ['ja', 'ru'])

        receptor_out = self.perceptor("Как перевести salut ca va с французского")
        self.assertEquals(receptor_out['phrase_to_translate'], "salut ca va")
        self.assertEquals(receptor_out['target_language_code_candidates'], ["ru"])

        receptor_out = self.perceptor("как переводится anticipatory")
        self.assertEquals(receptor_out['phrase_to_translate'], "anticipatory")
        self.assertEquals(receptor_out['detected_phrase_to_translate_language'], "en")
        self.assertIn("ru", receptor_out['target_language_code_candidates'])


        receptor_out = self.perceptor("что значит фраза Per aspera ad astra")
        self.assertEquals(receptor_out['phrase_to_translate'], "Per aspera ad astra")
        self.assertIn("ru", receptor_out['target_language_code_candidates'])

        # TODO
        lines = """
                             
                
                
                как будет по русски have
                как по русски будет to
                перевод слова дом на английский
                вайлдберриз перевод слова с английского
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
                перевод слова с английского going
                перевод английского слова where
                перевод английского слова live
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
                """

    def test_negatives(self):
        """

        Returns:

        """
        # TODO
        negatives = """
как по русски петь частушки
транскрипция и перевод слова дети английский
"""

        receptor_out = self.perceptor("что значит разгосударствление")
        self.assertFalse(receptor_out)

        receptor_out = self.perceptor("что означает мем")
        self.assertFalse(receptor_out)

        receptor_out = self.perceptor("перевод английских фунтов в американские доллары")
        self.assertFalse(receptor_out)

        receptor_out = self.perceptor("переведи 100 рублей Борису")
        self.assertFalse(receptor_out)

        receptor_out = self.perceptor("как перевести деньги в биткоины")
        self.assertFalse(receptor_out)

        receptor_out = self.perceptor("самые распространенные английские слова с переводом")
        self.assertFalse(receptor_out)

        receptor_out = self.perceptor("произношение английских слов слушать онлайн с переводом")
        self.assertFalse(receptor_out)
        receptor_out = self.perceptor("английские слова из 4 букв с переводом")
        self.assertFalse(receptor_out)
        receptor_out = self.perceptor("500 английских слов с переводом и транскрипцией")
        self.assertFalse(receptor_out)
        receptor_out = self.perceptor("часто употребляемые английские слова с переводом")
        self.assertFalse(receptor_out)




if __name__ == "__main__":
    unittest.main()
