################# Universal Import ###################################################
import sys
import os
SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SELF_DIR)))
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django
django.setup()

import pprint

from translator_skill.translator_intents_receptor.translator_perceptor.translate_intent_perceptor import \
    TranslatePerceptor, RegexpTranslatePerceptor

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

negative_samples = """
как по русски петь частушки

транскрипция и перевод слова дети английский
"""


if __name__=="__main__":
    rtp = RegexpTranslatePerceptor()
    pp = pprint.PrettyPrinter(indent=4)

    for each_line in lines.splitlines():
    # for each_line in negative_samples.splitlines():
        pp.pprint(each_line)
        receptor_out = rtp(each_line)
        pp.pprint(receptor_out)
        pp.pprint("__")
        import ipdb; ipdb.set_trace()
    pp.pprint(rtp("переведи слово задница"))
    #print()
    import ipdb; ipdb.set_trace()
    #rtp("переведи слово задница")