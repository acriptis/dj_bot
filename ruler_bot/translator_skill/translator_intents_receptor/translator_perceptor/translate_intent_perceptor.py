# -*- coding: utf-8 -*-
from components.slots.slots_factory import SlotsFactory

TARGET_PATTERN_NA_ANGLIISKIY = r"на (англи[ий]?ски[ий]|рус(с)?ки[ий]|испански[ий]|португальски[ий]|японски[ий]|французски[ий])"
TARGET_PATTERN_PO_ANGLIISKI = r"по(\-| )(англи[ий]?ски|рус(с)?ки|испански|португальски|японски|французски)"
TARGET_PATTERN_RUDE_NA_ANGLIISKOM = r"на (англи[ий]?ск|рус(с)?к]|испанск|португальск|японск|французск)ом"

SOURCE_PAT_S_ANGLIISKIGO = r"(с )?((англи(и|й)?ского)|(рус(с)?кого)|(испанского)|(португальского)|(японского)|(французского))( языка)?"
SOURCE_PAT_ANGLIISKOE_SLOVO = r"(англи[ий]?ское|рус(с)?кое|испанское|португальское|японское|французское)( слово)?"
SOURCE_PAT_ANGLIISKAYA_FRAZA = r"(англи[ий]?ская|рус(с)?кая|испанская|португальская|японская|французская)( фраза)?"


class TranslatePerceptor():

    intent_phrases = [
        "переведи на",
        "переведи слово",
        "переведи фразу",
        "переведи с английского",
        "переведи с англииского",
        "переведи с русского",
        "как по английски будет",
        "что означает слово",
        "что означает фраза",
        "что значит",
        "как по английски сказать",
        "как по англиски сказать",
        "как по англииски сказать",
        "Как с испанского перевести",
        "как переводится слово",
        "как переводится",
        "как перевести",
        "как будет по русски"
        "как по русски будет"
    ]

    def __init__(self):
        self.language_slot = SlotsFactory.produce_categorical_slot(
            name="language_entity",
            questioner=None,
            categories_domain_specification={
                "en": ["английский", "английски", "англииски", "инглиш", "английского", "английском"],
                "ru": ["русский", "руский", "русски", "русского" "ru"],
                "pt": ["португальский", "португальскии", "порту", "португальского", "pt"],
                "es": ["испански", "испанского", "эспаньол"],
                "ja": ["японский", "японскии", "японского", "японском"],
                "fr": ["французский", "французскии", "французского", "французском"]
            }
        )

    # def check_match(self, text, *args, **kwargs):

    def __call__(self, text, *args, **kwargs):
        # we need to detect intent by phrases:
        matched_intent_pattern = None
        text_lower = text.lower()
        for each_int_pattern in self.intent_phrases:

            if each_int_pattern.lower() in text_lower:
                matched_intent_pattern = each_int_pattern
                break
        else:
            # no intent match
            return False

        # intent detected lets extract languages:
        language_entities = self.language_slot.recept(text)
        print("matched_intent_pattern:")
        print(matched_intent_pattern)
        print("language entities:")
        print(language_entities)

        # now we can grasp residual phrase:
        print("text")
        print(text)
        # import ipdb; ipdb.set_trace()
        phrase_to_translate = text_lower.replace(matched_intent_pattern, "").strip()

        print(text)
        out_dict = {
            "text": text,
            'phrase_to_translate': phrase_to_translate,
            'matched_intent_segment': matched_intent_pattern,
            'language_entities': language_entities
        }
        return out_dict

from components.matchers.matchers import RegExpGroupMatcher


class RegexpTranslatePerceptor(TranslatePerceptor):
    # phrases that allow to distill candidates.
    # some of this phrases may not be real triggers for translation intent:
    # Ex.: "что значит слово kitchen", "что значит слово интеграл"

    # it is not easy to understand, it easy to fail, it impossible to support:
    intent_phrases_regexp = [
        r"переведи (" + TARGET_PATTERN_NA_ANGLIISKIY + r")?( слово| фразу)?",
        r"переведи( слово| фразу)?( на (англи[ий]?ски[ий]|рус(с)?ки[ий]|испански[ий]|португальски[ий]|японски[ий]|французски[ий]))?",

        r"переведи "+SOURCE_PAT_S_ANGLIISKIGO+r"( слово)?",
        r"как "+TARGET_PATTERN_PO_ANGLIISKI+r"( сказать| будет| пишется)?",
        r"как "+TARGET_PATTERN_PO_ANGLIISKI+r"( сказать| будет| пишется)?",
        r"Как с? (англи[ий]?ского|рус(с)?кого|испанского|португальского|японского|французского)( языка)? перевести",
        r"как переводится( слово| фраза)?",
        r"как перевести( слово| фразу)?",
        r"как будет по русски",
        r"как по русски будет",

        # min pattern: перевод с английского
        r"перевод\b( "+SOURCE_PAT_S_ANGLIISKIGO+r")( "+TARGET_PATTERN_NA_ANGLIISKIY+r"( язык)?)?( слов(о|а)?| фраза)?",

        # min pattern: перевод на английский
        r"перевод\b( "+SOURCE_PAT_S_ANGLIISKIGO+r")?( "+TARGET_PATTERN_NA_ANGLIISKIY+r"( язык)?)( слов(о|а)?| фраза)?",

        # min pattern: перевод слова
        r"перевод\b( "+SOURCE_PAT_S_ANGLIISKIGO+r")?( "+TARGET_PATTERN_NA_ANGLIISKIY+r"( язык)?)?( слов(о|а)?| фраза)",

        # min pattern: перевод слова
        # r"перевод\b ?"+SOURCE_PAT_S_ANGLIISKIGO+r"( слов(о|а)?)?",
        # r"перевод\b ?"+SOURCE_PAT_S_ANGLIISKIGO+r"( слово)?"+r"(\w+)( на (русский|англи(й|и)?ски(и|й)|испански(й|и)|португальский|японский)( язык)?)?",
        # r"перевод\b( слова| фразы)",
        # to avoid match on defintions requests we add English words templetes at the end [a-fA-F ]+:
        r"Что значит( слово| фраза)?",
        r"Что значит( слово| фраза)? (?=[a-fA-F ]+)",
        r"Что означает( слово| фраза)? (?=[a-fA-F ]+)",
        r"как " + TARGET_PATTERN_NA_ANGLIISKIY +r"( язык)?" r" перевести( слово| фразу)?",
        # TODO add accented letters for french, spansih portuguese, german?
    ]

    def match_intent(self, text, intent_patterns):

        regm = RegExpGroupMatcher(intent_patterns)
        match = regm(text)
        return match

    def match_target_language(self, text):
        """Given a text it search phrases like: на русккий, на англисйский
        """

        target_language_patterns = [
            TARGET_PATTERN_NA_ANGLIISKIY,
            TARGET_PATTERN_PO_ANGLIISKI,
            TARGET_PATTERN_RUDE_NA_ANGLIISKOM
        ]
        return self.match_language_role_patterns(text, target_language_patterns)

    def match_source_language(self, text):
        """Given a text it search phrases like: с русккого, с англисйского, английское (слово)
        """

        language_patterns = [
            SOURCE_PAT_S_ANGLIISKIGO,
            SOURCE_PAT_ANGLIISKOE_SLOVO,
            SOURCE_PAT_ANGLIISKAYA_FRAZA,
        ]
        return self.match_language_role_patterns(text, language_patterns)

    def match_language_role_patterns(self, text, language_role_patterns):
        """Given a text it search patterns of language role (target language or source language)
        and appends language entities
        """

        language_role_matcher = RegExpGroupMatcher(language_role_patterns)
        language_role_match = language_role_matcher.check_match(text)
        if language_role_match:
            # try to extract language
            language_entities = self.language_slot.recept(language_role_match['matched_text_segment'])
            language_entities = [*set(language_entities)]
            language_role_match['language entities'] = language_entities
        return language_role_match

    def __call__(self, text, *args, **kwargs):
        """
        The method implements main logic of perception algorithm:

        1. Detects intent if it triggers then launch cascade of processes of analysis (2,... ).
            If no match exit algorithm
        2. Extract Source language specification (переведи с английского)
        3. Extract Target language specification (переведи на японский)
        4. Extract Languages (that may be not matched by Target & Source Receptors)
        5. Strip out Intent segment, Languages segments.
        6. Interpret residual part of the string as PhraseToTranslate



        Args:
            text:
            *args:
            **kwargs:

        Returns: False or dict with analysis results:

            analysis results example:
                For input text: "перевод слова done с английского на русский"

                Returned document:
                    {
                        'language_entities': ['en', 'ru', 'ru'],
                        'matched_intent_segment': <_sre.SRE_Match object; span=(0, 13), match='перевод слова'>,
                        'phrase_to_translate': 'done',
                        'source_language_match': {   'language entities': ['en'],
                                                     'match': <_sre.SRE_Match object; span=(19, 32), match='с английского'>,
                                                     'matched_text_segment': 'с английского',
                                                     'triggered_pattern': '(с '
                                                                          ')?((англи(и|й)?ского)|(рус(с)?кого)|(испанского)|(португальского)|(японского)|(французского))( '
                                                                          'языка)?( слово)?'},
                        'target_language_match': {   'language entities': ['ru'],
                                                     'match': <_sre.SRE_Match object; span=(33, 43), match='на русский'>,
                                                     'matched_text_segment': 'на русский',
                                                     'triggered_pattern': 'на '
                                                                          '(англи[ий]?ски[ий]|рус(с)?ки[ий]|испански[ий]|португальски[ий]|японски[ий]|французски[ий])'},
                        'text': 'перевод слова done с английского на русский'}

        """

        print("text")
        print(text)

        matched_resp = self.match_intent(text, self.intent_phrases_regexp)
        if matched_resp:
            print("Matched!")
            # matched_intent_triggered_pattern = matched_resp['triggered_pattern']
            matched_intent_pattern = matched_resp['match']
            matched_substring = matched_resp['matched_text_segment']
        else:
            #import ipdb; ipdb.set_trace()
            #print("Nothing matched")
            return False
        print("translate command matched_substring:")
        print(matched_substring)

        source_matches = self.match_source_language(text)
        print("source_matches:")
        print(source_matches)

        target_matches = self.match_target_language(text)
        print("target_matches:")
        print(target_matches)

        # intent detected lets extract languages:
        language_entities = self.language_slot.recept(text)
        # deduplicate
        language_entities=[*set(language_entities)]

        print("language entities:")
        print(language_entities)

        #############################################################################
        # Stripping phrase to translate
        # now we can grasp residual phrase:
        # strip intent substring:
        phrase_to_translate = text.replace(matched_substring, "").strip()

        # we need to infer target language candidates:
        # most of the time it is target_matches' language entities (if they were extracted)
        # but sometimes it may fail so we append other lang codes as well.
        target_language_code_candidates = []

        # if phrase to translate still contains language entities we should strip it out
        if source_matches:
            phrase_to_translate = phrase_to_translate.replace(source_matches['matched_text_segment'], "").strip()
        if target_matches:
            phrase_to_translate = phrase_to_translate.replace(target_matches['matched_text_segment'], "").strip()
            # target matches must be first in candidates list:
            target_language_code_candidates += target_matches['language entities']

        # End Stripping phrase to translate
        #############################################################################
        # dict to output:
        out_dict = {}

        #### Detect target language candidates in non explicit cases
        if not target_language_code_candidates:
            # target is not detected, we should infer it.

            # assume that detected base language is the target language when it is not provided
            # explicitly and if it is not same language as phrase to translate language.

            # Potentially we may need to extend inference to let user use target
            # language specified in previous utterances of dialog.

            ### Bing
            from translator_skill.translator_service.bing_language_translator_service import \
                BingTranslatorService
            bts = BingTranslatorService()
            # bing_results = bts.detect_language(phrase_to_translate)
            detected_base_language = bts.detect_language(matched_substring)
            out_dict['detected_base_language'] =detected_base_language
            # print(f"bing_results for {matched_substring}")
            # print(detected_base_language)
            # if detected base language is the same as language of phrase to translate then we need
            # another variant
            detected_phrase_to_translate_language = bts.detect_language(phrase_to_translate)
            out_dict['detected_phrase_to_translate_language'] = detected_phrase_to_translate_language
            # print(f"bing_results for {phrase_to_translate}")
            # print(bing_results)
            language_entities.append(detected_base_language)
            if detected_base_language == detected_phrase_to_translate_language:
                # grasp language entites or use default variant?
                # import ipdb; ipdb.set_trace()
                # lets try to add uniqe language entities that are not the language of phrase
                # to translate
                for each_lang_ent in language_entities:
                    if detected_phrase_to_translate_language != each_lang_ent:
                        target_language_code_candidates.append(each_lang_ent)

            else:
                target_language_code_candidates.append(detected_base_language)
                language_entities.append(detected_phrase_to_translate_language)
            # # TODO refactor hardcoding defaults?
            # if not target_language_code_candidates:
            #     # if still no candidates then add default languages:
            #     if detected_phrase_to_translate_language == "ru":
            #         target_language_code_candidates.append("en")
            #     if detected_phrase_to_translate_language == "en":
            #         target_language_code_candidates.append("ru")
            #

        ####################################################################################
        ## Filter out wrong intents
        # final validation of intent to drop matches to "перевод", "перевод денег",
        # "переведи английские фунты в евро"
        if not target_language_code_candidates:
            # if still no target_language_code_candidates we may reject this intent
            print("WARNING: target_language_code_candidates are not inferred from message! "
                  "Rejecting translation or should we ask user about target language? ")
            out_dict.update({
                "text": text,
                'phrase_to_translate': phrase_to_translate,
                'matched_intent_segment': matched_intent_pattern,
                'matched_intent_triggered_pattern': matched_resp['triggered_pattern'],
                'language_entities': language_entities,
                'source_language_match': source_matches,
                'target_language_match': target_matches,
                'target_language_code_candidates': target_language_code_candidates
            })
            print(out_dict)
            # import ipdb; ipdb.set_trace()
            return False
        ####################################################################################
        print("target_language_code_candidates")
        print(target_language_code_candidates)
        print("phrase_to_translate:")
        print(phrase_to_translate)

        out_dict.update({
            "text": text,
            'phrase_to_translate': phrase_to_translate,
            'matched_intent_segment': matched_intent_pattern,
            'matched_intent_triggered_pattern': matched_resp['triggered_pattern'],
            'language_entities': language_entities,
            'source_language_match': source_matches,
            'target_language_match': target_matches,
            'target_language_code_candidates': target_language_code_candidates
        })
        return out_dict
