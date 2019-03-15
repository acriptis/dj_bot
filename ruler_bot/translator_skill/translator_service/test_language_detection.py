"""
Here is a snippet comparing different language detectors and their problems

Bing is the best in comparison with free libraries: langdetect, pycld2
"""
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

phrase_to_translate = "pedaço"
matched_substring = "Что значит слово"

# does not match portuguese phrase, but matches russian
import pycld2
results = pycld2.detect(phrase_to_translate)
results2 = pycld2.detect(matched_substring)
print(f"pycld2 results for {phrase_to_translate}")
print(results)
print(f"pycld2 results for {matched_substring}")
print(results2)

# does not match russian:
from langdetect import detect_langs
#https://pypi.org/project/langdetect/
source_phrase_langs = detect_langs(phrase_to_translate)
#print(source_phrase_langs)
#print(source_phrase_langs[0].lang)
### Pycld2

### Lang detect
intent_command_langs = detect_langs(matched_substring)
print(f"langdetect results for {phrase_to_translate}")
print(source_phrase_langs)
print(f"langdetect results for {matched_substring}")
print(intent_command_langs)

### Bing
from translator_skill.translator_service.bing_language_translator_service import \
    BingTranslatorService
bts = BingTranslatorService()
bing_results = bts.detect_language(phrase_to_translate)
bing_results2 = bts.detect_language(matched_substring)
print(f"bing_results for {phrase_to_translate}")
print(bing_results)
print(f"bing_results for {matched_substring}")
print(bing_results2)

### GoogleTrans
### GoogleTrans
from googletrans import Translator
translator = Translator()
gres1 = translator.detect(phrase_to_translate)
gres2 = translator.detect(matched_substring)
print(f"googletrans for {phrase_to_translate}")
print(gres1)
print(f"googletrans for {matched_substring}")
print(gres2)# TODO check
# https://pypi.org/project/googletrans/