# -*- coding: utf-8 -*-
from deeppavlov import build_model


class LanguageTermReceptor():
    """
    Receptor detecting intents for translation
    """
    def __init__(self, config_path=None):
        if not config_path:
            config_path = "/home/alx/Cloud/DeepPavlov/dj_bot/ruler_bot/translator_skill/translator_intents_receptor/translator_intents_dataset/translator_translation_intents_receptor_config.json"
        self.model = build_model(config_path)

    def __call__(self, signal_data, *args, **kwargs):
        """
        Receptor consumes not batches but items, so we make list wrapping-unwrapping here
        """
        assert 'text' in signal_data

        result_list = self.model([signal_data['text']])
