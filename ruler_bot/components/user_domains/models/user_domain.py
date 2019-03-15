# -*- coding: utf-8 -*-
from mongoengine import *
from components.deep_pavlov_agent_state.models import User, Dialog, Human
from components.dialog_management.agenda import Agenda


class UserDomain(Document):
    """The Document which stores state of the dialog with particular user
    """
    meta = {'strict': False}
    # we need to emulate user context:
    user_id = StringField(required=True)

    # create user dialog and push the message
    # if you want unique dialog for each user uncomment this:
    # self.userdialog, _ = UserDialog.objects.get_or_create(target_user=self.user)

    dialog = ReferenceField(Dialog)

    # dialog_plan = ReferenceField(DialogPlan)

    # ### #######################################################
    # ### Agenda #######################################################

    agenda = ReferenceField(Agenda, required=False)

    #queue_of_tasks = []
    #
    ## list of urgent tasks, they must be started before reaskings:
    #urgent_slot_tasks = []

    ####################################
    # filled slots of the user domain:
    memory = DictField(required=False, default={})

    ############################################
    # TODO Agenda loop DOCumentation

    # dictionary for callback functions which must be called after particular interactions completed
    callbacks_on_completion_of_interactions = {}
    # ^^ TODO delegate task management to celery?

    callbacks_on_completion_of_slots = {}
    # TODO delegate listeners functionality to EventProcessingBus?
    # self.callbacks_on_completion_of_interactions = {
    #     "<interaction_name>": [cb_fn1, cb_fn2...]
    # }

    # hacky storage to avoid dead callbacks (garbage Collected)
    _callbacks_storage = []

    # temporary attribute for utterances produced by Skills before emitting to Agent PostProcessing
    pending_utterances = ListField(StringField(required=False), default=[], required=False)
    #
    # user_slot_processes = ListField(UserSlotProcess)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # we need to save model because user_domain_manager creates persistent signals
        self.save()

        # from components.signal_reflex_routes.models.signals import UserMessageSignal
        # self.user_message_signal, _ = UserMessageSignal.get_or_create(self)



        # initilize runtime manager (user domain manager):
        # self.udm = self.get_user_domain_controller()
        #
        # init DialogPlanner
        # self.DialogPlanner = DialogPlanner(self)

        # self.MemoryManager = MemoryManager(self)

        # helper for interactions
        # self.im = InteractionsManager(self)

        # slot specifications:
        # self.sm = SlotsManager(self)

        # slot + user data management:
        # self.uspm = UserSlotProcessesManager(self)

        # all interactions and skills must connect its receptors to Receptors Pool
        # for receiving signals of UserMessages
        # self.receptors_pool = ReceptorsPool(self)

    @property
    def user_message_signal_pattern(self):
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        sp, _ = SignalPattern.get_or_create_strict(signal_type="UserMessageSignal", user_domain=self)
        return sp

    @property
    def user_message_signal(self):
        from components.signal_pattern_reflex.signal import Signal
        # self.user_message_signal_pattern = SignalPattern(signal_type="UserMessageSignal", user_domain=self).save()
        user_message_signal = Signal(signal_type="UserMessageSignal", user_domain=self)
        return user_message_signal
    #
    #@property
    #def receptors
    @classmethod
    def get_or_create_user_domain(cls, user_id):
        """Gets or creates an object from init specification

        The method creates a schema of user domain if it is first time launch or restores
            UserDomain from persistent storage for particular user (if it was created before).

        Args:
            user_id: identifier of user

        Returns:
            tuple: (instance:cls, is_created:bool)
                instance - is an object of the Class provided for arguments.
                is_created - True if the instance created from provided arguments, False otherwise

        Raises:
            Exception: For multiple instances of the provided filter.

        """
        if isinstance(user_id, int):
            user_id = str(user_id)
        results = UserDomain.objects(user_id=user_id)

        if results:
            if len(results) > 1:
                raise Exception(
                      f"Multiple instances found for {cls.__name__}!")
            elif len(results) == 1:
                return results[0], False
        else:

            # create dialog model
            ########################################################

            # Create BOT
            bot_user, is_created = User.get_or_create(user_type='bot')
            bot_user.save()
            human_user, is_created = Human.get_or_create(username=user_id)
            human_user.save()

            dialog_obj = Dialog(utterances=[], users=[bot_user, human_user])
            dialog_obj.save()

            agenda =Agenda()
            agenda.save()
            ########################################################
            instance = cls(user_id=user_id, dialog=dialog_obj, agenda=agenda)
            instance.save()
            return instance, True

    @property
    def udm(self):
        return self.get_user_domain_controller()

    def get_target_user(self):
        """

        Returns: Human User

        """
        human_user, is_created = Human.get_or_create(username=self.user_id)
        return human_user

    def get_user_domain_controller(self):
        from components.user_domains.user_domain_controller import UserDomainController
        return UserDomainController(self)

    @classmethod
    def from_user_id(cls, user_id):
        """
        Given user id it constructs UserDomainController and related UserDomain (gets or creates)
        Args:
            user_id:

        Returns: ready to go UserDomainController

        """
        user_domain, is_created = UserDomain.get_or_create_user_domain(user_id)
        return user_domain

    def restart_userdomain(self):
        """
        Clean data from user domain to allow scenarios to be restarted
        Returns:

        """
        # delete user processes:
        from components.user_processes.user_slot_process import UserSlotProcess
        UserSlotProcess.objects(user_domain=self).delete()
        from components.user_processes.user_interaction_process import UserInteractionProcess
        UserInteractionProcess.objects(user_domain=self).delete()

        # remove signal patterns and reflexes
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        sps = SignalPattern.objects(user_domain=self)
        if sps:
            from components.signal_pattern_reflex.signal_pattern_reflex_route import SignalPatternReflexRoute
            SignalPatternReflexRoute.objects(signal_pattern__in=sps).delete()
            sps.delete()
        from components.signal_pattern_reflex.reflex import Reflex
        # from components.signal_pattern_reflex.reflex import Reflex, ObjectMethodReflex, ReceptorReflex
        reflexes = Reflex.objects(user_domain=self)
        if reflexes:
            # import ipdb; ipdb.set_trace()
            SignalPatternReflexRoute.objects(reflex__in=reflexes).delete()
            reflexes.delete()
        # import ipdb; ipdb.set_trace()

        # ObjectMethodReflex.objects(user_domain=self).delete()
        # ReceptorReflex.objects(user_domain=self).delete()

        # delete dialog to avoid prehistory recepts:
        from components.user_processes.user_interaction_process import UserInteractionProcess
        self.dialog.utterances = []
        self.dialog.save()
        self.memory = {}
        self.agenda.reset()
        self.save()

        return True
