import os, requests, uuid, json

from translator_skill.translator_service.language_translator_service import \
    LanguageTranslatorService


class BingTranslatorService(LanguageTranslatorService):
    def __init__(self):

        # Checks to see if the Translator Text subscription key is available
        # as an environment variable. If you are setting your subscription key as a
        # string, then comment these lines out.
        if 'TRANSLATOR_TEXT_KEY' in os.environ:
            self.subscriptionKey = os.environ['TRANSLATOR_TEXT_KEY']
        else:
            raise Exception('Environment variable for TRANSLATOR_TEXT_KEY is not set.')
            # exit()
        # If you want to set your subscription key as a string, uncomment the next line.
        # subscriptionKey = 'put_your_key_here'

    def translate(self, phrase, target_language_candidates_codes):
        """

        Args:
            phrase: phrase to translate

            target_language_candidates_codes: language codes for the target language candidates,
                you may provide 2 languages and it decide how to translate it

            language codes of BingTranslator:


        Returns:
            string with translation or None
        """
        # If you encounter any issues with the base_url or path, make sure
        # that you are using the latest endpoint:
        # https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
        base_url = 'https://api.cognitive.microsofttranslator.com'
        path = '/translate?api-version=3.0'
        # params = f"&to={source_lang_code}&to={target_lang_code}"
        params = ""
        target_lang_codes = target_language_candidates_codes
        for each_target_lang_code in target_lang_codes:
            params += f"&to={each_target_lang_code}"
        constructed_url = base_url + path + params

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscriptionKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # You can pass more than one object in body.
        body = [{
            'text': phrase
        }]
        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()

        ### Decorate response for universal format ################################################
        try:
            for each_translation_variant in response[0]['translations']:
                # select reposnse that is not the same as input phrase (to avoid RU-RU translation):
                if each_translation_variant['text'] != phrase:
                    simple_response = each_translation_variant['text']
                    break
            else:
                raise Exception(f"No Translation for the phrase: {phrase}")

            return simple_response
        except Exception as e:
            print(e)
            print("response")
            print(response)
            print("request")
            print(request)
            # import ipdb; ipdb.set_trace()
            print(request)
            raise e

    def detect_language(self, phrase):
        """
        Given a phrase returns a language code of the language detected in phrase

        returns a first candidate or raises Exception
        Args:
            phrase:

        Returns:

        """
        # If you encounter any issues with the base_url or path, make sure
        # that you are using the latest endpoint:
        # https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-detect
        base_url = 'https://api.cognitive.microsofttranslator.com'
        path = '/detect?api-version=3.0'
        constructed_url = base_url + path

        headers = {
            'Ocp-Apim-Subscription-Key': self.subscriptionKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # You can pass more than one object in body.
        body = [{
            'text': phrase
        }]
        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()

        print(json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False,
                         separators=(',', ': ')))

        ### Decorate response for universal format ################################################
        try:
            # get first candidate:
            detected_language_code = response[0]['language']
            return detected_language_code
        except Exception as e:
            print("Exception in BingTranslatorService.detect_language")
            print(e)
            print("response")
            print(response)
            print("request")
            print(request)
            import ipdb;
            ipdb.set_trace()
            print(request)
            raise e

    def get_languages(self):
        """
        dict_keys(['af', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el',
        'en',
        'es',
        'et', 'fa', 'fi', 'fil', 'fj', 'fr', 'he', 'hi', 'hr', 'ht', 'hu', 'id', 'is', 'it',
        'ja', 'ko', 'lt', 'lv', 'mg', 'ms', 'mt', 'mww', 'nb', 'nl', 'otq', 'pl',
        'pt', 'ro',
        'ru', 'sk', 'sl', 'sm', 'sr-Cyrl', 'sr-Latn', 'sv', 'sw', 'ta', 'te', 'th', 'tlh',
        'to', 'tr', 'ty', 'uk', 'ur', 'vi', 'yua', 'yue', 'zh-Hans', 'zh-Hant'])
        Returns:

        """
        # If you encounter any issues with the base_url or path, make sure
        # that you are using the latest endpoint:
        # https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-languages
        base_url = 'https://api.cognitive.microsofttranslator.com'
        path = '/languages?api-version=3.0'
        constructed_url = base_url + path

        headers = {
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        request = requests.get(constructed_url, headers=headers)
        response = request.json()

        print(json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False,
                         separators=(',', ': ')))
        import ipdb; ipdb.set_trace()

        return response
