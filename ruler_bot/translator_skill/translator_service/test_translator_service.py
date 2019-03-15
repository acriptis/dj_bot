# -*- coding: utf-8 -*-
import unittest
################# Universal Import ###################################################
import sys
import os


SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SELF_DIR))
PREROOT_DIR = os.path.dirname(ROOT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django

django.setup()

from translator_skill.translator_service.bing_language_translator_service import \
    BingTranslatorService

if __name__=="__main__":
    bt = BingTranslatorService()
    response = bt.translate("вертолет летит вчера", ["en", "ru"])
    print(response)
    import ipdb; ipdb.set_trace()
    print(response)

