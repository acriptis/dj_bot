from components.interactions.models import Interaction
from translator_skill.translator_service.bing_language_translator_service import \
            BingTranslatorService
from translator_skill.translator_intents_receptor.translator_perceptor.translate_intent_perceptor import \
    TranslatePerceptor


class TranslatorInteraction(Interaction):
    def __init__(self, *args, **values):
        """Domain construction
        """
        super().__init__(*args, **values)
        # self.tp = TranslatePerceptor()

        self._connect_receptor(receptor_type="RegexpTranslatePerceptor",
                               init_args={},
                               callback_fn=self.start)

        # # ###################################################
        # from components.receptors.models import Receptor
        # # from components.signal_reflex_routes.models.signals import ReceptorTriggeredSignal
        # self.tp, created = Receptor.get_or_create(
        #     class_name='RegexpTranslatePerceptor', init_args={})
        # # ###################################################
        #
        # from components.signal_pattern_reflex.signal_pattern import SignalPattern
        # sp, _ = SignalPattern.get_or_create_strict(signal_type="UserMessageSignal")
        # sp.connect(self.tp.__call__)
        #
        # receptor_trigger_signal_pattern, _ = SignalPattern.get_or_create_strict(
        #     signal_type="ReceptorTriggeredSignal", receptor=self.tp)
        # # we need to save self before creating persistent signal-reflex connections:
        # self.save()
        # receptor_trigger_signal_pattern.connect(self.start)
        # # connect translator receptor with start method which receives data from perceptor and
        # # routes it to translation service

    def start(self, *args, **kwargs):
        print(kwargs)
        # import ipdb; ipdb.set_trace()
        assert 'phrase_to_translate' in kwargs
        assert 'language_entities' in kwargs
        assert 'target_language_code_candidates' in kwargs

        translation = self.translate_phrase(
            phrase_to_translate=kwargs['phrase_to_translate'],
            language_entities=kwargs['target_language_code_candidates'])
        if translation:
            kwargs['user_domain'].udm.DialogPlanner.sendText(translation)
        else:
            # write something like "I don't know how to translate this"?
            pass

    def translate_phrase(self, phrase_to_translate, language_entities):
        """
        returns translation string or None
        """

        bts = BingTranslatorService()
        if not language_entities:
            language_entities = ['ru', 'en']
        # elif len(language_entities)==1:
        #     # it often lacks russian language while being written in russian like:
        #     #{'text': 'перевод с английского слова better', 'phrase_to_translate': 'better',...
        #     if 'ru' not in language_entities:
        #         language_entities.append("ru")
        #     if 'en' not in language_entities:
        #         language_entities.append("en")
        try:
            translation = bts.translate(phrase_to_translate, language_entities)
            return translation
        except Exception as e:
            # translation exception may occur because of incorrect language entities
            # when translation is from the same language
            print(e)
            return None

    def connect_to_dataflow(self, udc):
        """
        makes preparations fpor particular UserDomain. Here we may attach special receptors for
        VIP Users

        Args:
            udc: UserDomainController
        """
        pass