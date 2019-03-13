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

from translator_skill.translator_intents_receptor.translator_perceptor.translate_intent_perceptor import \
    TranslatePerceptor, RegexpTranslatePerceptor

if __name__=="__main__":
    # tp = TranslatePerceptor()

    # print(tp("Как по английски будет мама"))

    # print(tp("Как с испанского перевести madre"))

    rtp = RegexpTranslatePerceptor()
    print(rtp("переведи слово задница"))
    import ipdb; ipdb.set_trace()
    rtp("переведи слово задница")