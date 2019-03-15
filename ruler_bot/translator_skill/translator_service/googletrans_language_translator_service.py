from translator_skill.translator_service.language_translator_service import \
    LanguageTranslatorService


class GoogleTransTranslatorService(LanguageTranslatorService):
    """
    This is not official google translator it is hacky web checker
    see:
        https://pypi.org/project/googletrans/
    """
    def __init__(self):

        from googletrans import Translator
        self._translator = Translator()
        # print(translator.detect('이 문장은 한글로 쓰여졌습니다.'))
        # gres1 = translator.detect(phrase_to_translate)
        # gres2 = translator.detect(matched_substring)
        # print(f"googletrans for {phrase_to_translate}")
        # print(gres1)
        # print(f"googletrans for {matched_substring}")
        # print(gres2)

    def translate(self, phrase, target_langs_codes):
        """

        # >>> translator.translate('안녕하세요.')
        # # <Translated src=ko dest=en text=Good evening. pronunciation=Good evening.>
        # >>> translator.translate('안녕하세요.', dest='ja')
        # # <Translated src=ko dest=ja text=こんにちは。 pronunciation=Kon'nichiwa.>
        # >>> translator.translate('veritas lux mea', src='la')
        # # <Translated src=la dest=en text=The truth is my light pronunciation=The truth is my light>
        Args:
            phrase:
            target_langs_codes:

        Returns:

        """
        results = self._translator.translate(phrase, dest=target_langs_codes[0])
        # TODO universalize results
        return results

    def detect_language(self, phrase):
        results = self._translator.detect(phrase)
        # TODO universalize results
        return results

    def get_languages(self):
        """
        Show supported languages
        Returns:

        """
        raise Exception("Not implemented")
