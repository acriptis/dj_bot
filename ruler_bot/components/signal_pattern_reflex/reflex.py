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
    # meta = {"abstract": True}
    meta = {"allow_inheritance": True}

    user_domain = ReferenceField(UserDomain, required=False)

    # Interaction object or UserSlotProcess object
    instance_locator = GenericReferenceField()

    # method of the interaction or slot
    method_name = StringField(required=False)

    def return_prepared_callback(self, *args, **kwargs):
        """
        Method is responsible for returning callback function from reflex persistent representation
        Returns:

        """
        # import ipdb; ipdb.set_trace()

        instance = self.instance_locator
        if isinstance(instance, Interaction):
            # interaction
            # import ipdb; ipdb.set_trace()

            # user_domain_controller = UserDomainController(self.user_domain)
            # user_domain_controller.im.
            # instance.connect_to_dataflow(user_domain_controller)
            print("Interaction callback")

        elif isinstance(instance, UserSlotProcess):
            print("UserSlotProcess callback")
            user_domain_controller = UserDomainController(self.user_domain)
            if not instance.slot:
                import ipdb; ipdb.set_trace()

                # we must init slot element as active object from slot codename:

                slot_codename = instance.slot_codename
                instance.slot = user_domain_controller.sm.slotname2instance[slot_codename]
                # import ipdb; ipdb.set_trace()

            # instance.connect_to_dataflow(user_domain_controller)
        elif isinstance(instance, Receptor):
            print(f"Receptor {instance} recept function")
            # print("Receptor recept function")
            # user_domain_controller = UserDomainController(self.user_domain)
            # import ipdb; ipdb.set_trace()

            # instance.connect_to_dataflow(user_domain_controller)

            # instance.connect_to_dataflow(user_domain_controller)
        elif isinstance(instance, AbstractTextMatcher):
            print("AbstractTextMatcher recept function")
            user_domain_controller = UserDomainController(self.user_domain)
            import ipdb; ipdb.set_trace()

            # instance.connect_to_dataflow(user_domain_controller)

            # instance.connect_to_dataflow(user_domain_controller)
        else:
            raise Exception("Unknown Reflex Object!")

        if not hasattr(instance, self.method_name):
            raise Exception("WARNING: Method does not exists!")
            # print()

        return getattr(instance, self.method_name)




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


class InteractionMethodReflex(ObjectMethodReflex):
    """
        Reflex for launching Methods of InteractionProcesses
    """

    def __call__(self, *args, **kwargs):
        # when reflex is called we need to retrieve an object and launch its method
        raise Exception(f"{self.__class__.__name__}.__call__: Implement me!")

    def return_prepared_callback(self, *args, **kwargs):
        # user_domain_controller = UserDomainController(self.user_domain)
        raise Exception(f"{self.__class__.__name__}.__call__: Implement me!")


class SlotProcessMethodReflex(ObjectMethodReflex):
    """
        Reflex for launching Methods of SlotProcesses

    TODO merge with InteractionMethodReflex?
    """

    def __call__(self, *args, **kwargs):
        # when reflex is called we need to retrieve an object and launch its method
        raise Exception(f"{self.__class__.__name__}.__call__: Implement me!")


class GenericFunctorReflex(Reflex):
    """
    Reflex that encapsulates any python function.
    """
    def __call__(self, *args, **kwargs):
        # when reflex is called we need to retrieve an object and launch its functor
        raise Exception(f"{self.__class__.__name__}.__call__: Implement me!")
