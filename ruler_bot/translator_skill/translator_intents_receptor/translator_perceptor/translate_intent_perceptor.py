from components.slots.slots_factory import SlotsFactory


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
                "en": ["английский", "английски", "англииски", "инглиш", "английского", "en"],
                "ru": ["русский", "руский", "русски", "русского" "ru"],
                "pt": ["португальский", "португальскии", "порту", "португальского", "pt"],
                "es": ["испански", "испанского", "эспаньол"],
                "jp": ["японский", "японскии", "японского", "jp"]
            },
            silent_value=["ru", "en"]
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


class RegexpTranslatePerceptor(TranslatePerceptor):
    intent_phrases_regexp = [
        "переведи( слово| фразу)?",
        "что означает слово",
        "что означает фраза",
        "что значит",
        "переведи на",
        "переведи с английского",
        "переведи с англииского",
        "переведи с русского",
        "как по английски сказать",
        "как по англиски сказать",
        "как по англииски сказать",
        "как по английски будет",
        "Как с испанского перевести",
        "как переводится( слово| фраза)?",
        "как перевести( слово| фразу)?",
        "как будет по русски",
        "как по русски будет",
        "перевод с английского( слово| фраза)?",
        "перевод( слова| фразы)?",

    ]

    def match_intent(self, text, intent_patterns):
        from components.matchers.matchers import RegExpGroupMatcher
        regm = RegExpGroupMatcher(intent_patterns)
        match = regm(text)
        return match

    def __call__(self, text, *args, **kwargs):

        matched_resp = self.match_intent(text, self.intent_phrases_regexp)
        if matched_resp:
            print("Matched!")
            matched_intent_pattern = matched_resp['match']
            matched_substring = matched_resp['matched_text_segment']
        else:
            print("Nothing matched")
            return False

        # intent detected lets extract languages:
        language_entities = self.language_slot.recept(text)
        print("matched_substring:")
        print(matched_substring)

        print("language entities:")
        print(language_entities)

        # now we can grasp residual phrase:
        print("text")
        print(text)
        phrase_to_translate = text.replace(matched_substring, "").strip()

        print("phrase_to_translate:")
        print(phrase_to_translate)
        out_dict = {
            "text": text,
            'phrase_to_translate': phrase_to_translate,
            'matched_intent_segment': matched_intent_pattern,
            'language_entities': language_entities
        }
        return out_dict
