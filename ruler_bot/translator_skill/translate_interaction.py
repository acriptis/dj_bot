from components.interactions.models import Interaction
from translator_skill.translator_intents_receptor.translator_perceptor.translate_intent_perceptor import \
    TranslatePerceptor


class TranslatorInteraction(Interaction):
    def __init__(self, *args, **values):
        """Domain construction
        """
        super().__init__(*args, **values)
        # self.tp = TranslatePerceptor()

        # ###################################################
        from components.receptors.models import Receptor
        # from components.signal_reflex_routes.models.signals import ReceptorTriggeredSignal
        self.tp, created = Receptor.get_or_create(
            class_name='RegexpTranslatePerceptor', init_args={})
        # ###################################################

        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        sp, _ = SignalPattern.get_or_create_strict(signal_type="UserMessageSignal")
        sp.connect(self.tp.__call__)

        receptor_trigger_signal_pattern, _ = SignalPattern.get_or_create_strict(
            signal_type="ReceptorTriggeredSignal", receptor=self.tp)
        # we need to save self before creating persistent signal-reflex connections:
        self.save()
        receptor_trigger_signal_pattern.connect(self.start)
        # connect translator receptor with start method which receives data from perceptor and
        # routes it to translation service

    def start(self, *args, **kwargs):
        print(kwargs)
        # import ipdb; ipdb.set_trace()
        assert 'phrase_to_translate' in kwargs

        translation = self.translate_phrase(kwargs['phrase_to_translate'], kwargs['language_entities'])
        if translation:
            kwargs['user_domain'].udm.DialogPlanner.sendText(translation)

    def translate_phrase(self, phrase_to_translate, language_entities):
        from translator_skill.translator_service.translator_service import BingTranslatorService
        bts = BingTranslatorService()
        if not language_entities:
            language_entities = ['ru', 'en']
        translation = bts.translate(phrase_to_translate, language_entities)
        return translation

    def connect_to_dataflow(self, udc):
        """
        makes preparations fpor particular UserDomain. Here we may attach special receptors for
        VIP Users

        Args:
            udc: UserDomainController
        """
        pass