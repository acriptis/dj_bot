# -*- coding: utf-8 -*-
################# Universal Import ###################################################
import sys
import os
SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SELF_DIR))
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django
django.setup()

from deeppavlov import configs, train_model
from deeppavlov import build_model


if __name__=="__main__":
    #ner_model = train_model(configs.ner.ner_few_shot_ru, download=True)
    #ner_model = train_model("/home/alx/Cloud/DeepPavlov/dj_bot/ruler_bot/translator_skill/translator_intents_receptor/translator_intents_dataset/translator_intents_receptor_config.json")
    # path_to_config = "/home/alx/Cloud/DeepPavlov/dj_bot/ruler_bot/translator_skill/translator_intents_receptor/translator_intents_dataset/translator_translation_intents_receptor_config.json"
    path_to_config = "/home/alx/Workspace/dj_bot/ruler_bot/translator_skill/translator_intents_receptor/translator_intents_dataset/translator_translation_intents_receptor_config.json"
    ner_model = train_model(path_to_config)
    import ipdb; ipdb.set_trace()
    print(ner_model(['Переведи на испанский слово мальчик']))
    ner_model.save()

def pa():

    ner_model = build_model(path_to_config)

