from mongoengine import *

from components.utils.mongoengine_get_or_create_mixin import MongoEngineGetOrCreateMixin


class Receptor(Document, MongoEngineGetOrCreateMixin):
    """
    Class for Receptors which may use different implementation of functions
    """
    meta = {
        'allow_inheritance':True
    }

    # user_domain = ReferenceField(UserDomain)

    # receptors are specified as classes in
    class_name = StringField(required=False)

    # args and kwargs for initialization of Receptor object
    # it may be phrases set for PhrasesMatcher or any other params
    init_args = DynamicField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initilize model
        self._initialize_model()

    def connect_to_dataflow(self, udc):
        self.udc = udc
        udc.receptors_pool.connect(self)

    def _initialize_model(self):
        """

        Returns:

        """
        model_class = self.classname2class(self.class_name)
        self._model_obj = model_class(**self.init_args)
        return self._model_obj

    def classname2class(self, classname):
        """

        Args:
            classname:

        Returns: class from classname

        """
        if classname == "PhrasesMatcher":
            # TODO make normal registry from receptor names into implementation classes!
            from components.matchers.matchers import PhrasesMatcher
            return PhrasesMatcher
        elif classname == "TranslatePerceptor":
            from translator_skill.translator_intents_receptor.translator_perceptor.translate_intent_perceptor import TranslatePerceptor
            return TranslatePerceptor
        elif classname == "RegexpTranslatePerceptor":
            from translator_skill.translator_intents_receptor.translator_perceptor.translate_intent_perceptor import RegexpTranslatePerceptor
            return RegexpTranslatePerceptor

    def __call__(self, *args, **kwargs):
        # if self._model_obj.check_match(*args, **kwargs):
        # import ipdb; ipdb.set_trace()

        result = self._model_obj(*args, **kwargs)
        if result:
            print(f"Receptor {self} Triggered!")
            user_domain = kwargs['user_domain']
            from components.signal_pattern_reflex.signal import Signal
            signal = Signal()
            payload = kwargs
            payload["receptor"] = self
            payload["signal_type"] = "ReceptorTriggeredSignal"
            print("payload:")
            print(payload)
            print("result:")
            print(result)
            # import ipdb; ipdb.set_trace()

            if isinstance(result, dict):
                payload.update(result)
            # import ipdb; ipdb.set_trace()
            signal.send(**payload)

        else:
            print("No match")

    def __str__(self):
        return f"Receptor: {self.class_name, self.init_args}"
