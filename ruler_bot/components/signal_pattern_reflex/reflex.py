from mongoengine import *

from components.receptors.models import Receptor
from components.user_domains.models import UserDomain
from components.user_domains.user_domain_controller import UserDomainController

#TODO delete such dependency?:
# Components for calling
from components.interactions.models import Interaction
from components.user_processes.user_slot_process import UserSlotProcess
from components.matchers.matchers import AbstractTextMatcher
from components.utils.mongoengine_get_or_create_mixin import MongoEngineGetOrCreateMixin


class Reflex(Document, MongoEngineGetOrCreateMixin):
    # meta = {"abstract": True}
    meta = {"allow_inheritance": True}

    def __call__(self, *args, **kwargs):
        cb_fn = self.return_prepared_callback(*args, **kwargs)
        return cb_fn(*args, **kwargs)
        # raise Exception(f"{self.__class__.__name__}.__call__: Implement me!")

    def return_prepared_callback(self, *args, **kwargs):
        """reflex may be a complex object which may require special initilization before
        callback function will be ready to use. This method implements all preparations of callback
        function from persistent reflex object.

        Before we call any callback we must initialize parent object and find method.

        Returns: callback which is ready for use in runtime context

        """
        raise Exception(f"{self.__class__.__name__}.__call__: Implement me!")

    @classmethod
    def receiver_fn_into_reflex(cls, receiver_fn):
        """Given a receiver function it creates a reflex

        Args:
            receiver_fn:

        Returns:

        """
        import types
        if isinstance(receiver_fn, types.MethodType):

            from components.signal_pattern_reflex.reflex import ObjectMethodReflex
            object_method_reflex, _ = ObjectMethodReflex.get_or_create(
                instance_locator=receiver_fn.__self__,
                method_name=receiver_fn.__name__)
            return object_method_reflex
        else:
            print(receiver_fn)
            import ipdb; ipdb.set_trace()

            raise Exception("Unsupported type of receiver")


class ObjectMethodReflex(Reflex):
    """
    Persistent objects method reflex
    """
    # meta = {"abstract": True}
    meta = {"allow_inheritance": True}

    # user_domain = ReferenceField(UserDomain, required=False)

    # Interaction object or UserSlotProcess object
    instance_locator = GenericReferenceField()

    # method of the interaction or slot
    method_name = StringField(required=False)

    def return_prepared_callback(self, *args, **kwargs):
        """
        Method is responsible for returning callback function from reflex persistent representation
        Returns:

        """
        instance = self.instance_locator
        if isinstance(instance, Interaction):
            print("Interaction callback")

        elif isinstance(instance, UserSlotProcess):
            print("UserSlotProcess callback")
            if not instance.slot:
                raise Exception(f"No slot instance in UserSlotProcess {instance}!")

        elif isinstance(instance, Receptor):
            print(f"Receptor {instance} recept function")

        elif isinstance(instance, AbstractTextMatcher):
            print("AbstractTextMatcher recept function")
            import ipdb; ipdb.set_trace()

        else:
            raise Exception("Unknown Reflex Object!")

        if not hasattr(instance, self.method_name):
            raise Exception("WARNING: Method does not exists!")
            # print()

        return getattr(instance, self.method_name)

    def __str__(self):
        return f"ObjectMethodReflex[instance: {self.instance_locator}, method: {self.method_name}]"


class ReceptorReflex(Reflex):
    """Receptor Reflex which is used to connect Receptors with

    """
    user_domain = ReferenceField(UserDomain)

    receptor = ReferenceField(Receptor)
    # # receptors are specified as classes in
    # class_name = StringField(required=False)
    #
    # # args and kwargs for initialization of Receptor object
    # # it may be phrases set for PhrasesMatcher or any other params
    # init_args = DynamicField(required=False)

    def return_prepared_callback(self, *args, **kwargs):
        """
        Method is responsible for returning callback function from reflex persistent representation
        Returns:

        """
        return self.receptor.__call__


class DynamicObjectMethodReflex(Reflex):
    """
    For reflexes which are restorable by module path, class name
    """
    # module_locator = StringField()
    # class_locator: 'aiml_skill.aimls_skill.AIMLSkill':
    class_locator = StringField()
    init_args = DictField(required=False)
    method_name = StringField(required=False, default="__call__")

    @classmethod
    def reflex_from_receiver(cls, receiver):

        clss = receiver.__self__.__class__
        module = clss.__module__
        class_locator = module +"." +clss.__name__

        reflex, _ = cls.get_or_create(class_locator=class_locator,
                                      method_name=receiver.__name__)
        return reflex

    def return_prepared_callback(self, *args, **kwargs):
        """
        Method is responsible for returning callback function from reflex persistent representation
        Returns:

        """
        from pydoc import locate
        class_of_obj = locate(self.class_locator)
        if self.init_args:
            instance = class_of_obj(**self.init_args)
        else:
            instance = class_of_obj()
        return getattr(instance, self.method_name)

    def __str__(self):
        return f"DynamicObjectMethodReflex[class_locator: {self.class_locator}, method: {self.method_name}, init_args={self.init_args}]"
