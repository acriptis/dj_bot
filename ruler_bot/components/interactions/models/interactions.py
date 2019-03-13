
import django.dispatch

from components.utils.mongoengine_get_or_create_mixin import MongoEngineGetOrCreateMixin


class AbstractInteraction():
    """
    Specification of Interaction That announces its exit to those who may be concerned

    Signal is available after initialization...
    """

    # Exit Gates Default Speicification:
    EXIT_GATE_OK = "ExitGate_Ok"

    # child Interactions must specify EXIT_GATES_NAMES_LIST, with exit gates
    # otherwise system import default list:
    base_EXIT_GATES_NAMES_LIST = [
        EXIT_GATE_OK
    ]
    # from list of EXIT_GATES_NAMES_LIST signals are generated into the dictoionary:
    # EXIT_GATES_SIGNALS

    @classmethod
    def get_name(cls):
        return cls.__name__

    def start(self, *args, **kwargs):
        raise Exception("NotImplemented")

    @classmethod
    def initialize(cls, ic, name=None, *args, **kwargs):
        """
        Interaction initialization requres:
        1. specify its name (And register it in the Interactions Registry)
        2. initilize EXIT GATES of the interaction.
            EXIT GATES are declared in implementation class, if not then default set of exit gates is assumed
            (the only: ExitGate_Ok)

        :param ic:
        :param name:
        :param args:
        :param kwargs:
        :return:
        """
        if not name:
            # default name is a name of class
            name = cls.__name__
        # import ipdb; ipdb.set_trace()

        intrctn = cls()

        intrctn.ic = ic

        # #########################################################################################
        # # Exit Gate Signals and Registry initialization
        intrctn.EXIT_GATES_SIGNALS = {}
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        intrctn.EXIT_GATES_SIGNAL_PATTERNS = {}

        if not hasattr(intrctn, 'EXIT_GATES_NAMES_LIST'):
            # TODO fix to support inheritance of ExitGates!
            # then import default Gates :
            intrctn.EXIT_GATES_NAMES_LIST = cls.base_EXIT_GATES_NAMES_LIST

        # now init signal objects for each exit gate:
        for each_exit_gate_name in intrctn.EXIT_GATES_NAMES_LIST:
            # create a signal object for each exit gate

            intrctn.EXIT_GATES_SIGNAL_PATTERNS[each_exit_gate_name], _ = SignalPattern.get_or_create_strict(
                signal_type="InteractionProcessCompletedSignal", interaction=intrctn,
                exit_gate=each_exit_gate_name
            )
            intrctn.EXIT_GATES_SIGNALS[each_exit_gate_name] = django.dispatch.dispatcher.Signal(
                providing_args=["userdialog"])

        intrctn._anti_garbage_collector_callbacks_list = []
        # END ExitGate Signals Initialization

        ########################################################################################
        intrctn.post_init_hook()

        return intrctn

from mongoengine import DynamicDocument, StringField, Document


class Interaction(Document, AbstractInteraction, MongoEngineGetOrCreateMixin):
    """
    Base ORM model for interaction specification
    """
    name = StringField(max_length=200)

    ##################################################################
    # Exit Gates declaration:
    # default_exit_gate = ExitGate(EXIT_GATE_OK)

    # Exit Gates Specification Problem: how to specify exit gates?
    # requirements:
    # 1. derived classes should inherit base exit gates
    # 2. derived classes can use default exit gate specification
    # 3. each instance of interaction has its own exit gates instances
    #  need to initialize signals registry dynamically to avoid crossing of signals between interaction instances

    # Solution approaches:
    # 1. for custom Interaction class descriptor set list attribute  with names of all exit gates
    #       problem: if class inherits from some base class it must redefine all exit gates
    #           (even if it does not affect related functionality )
    # 2. for custom Interaction class descriptor set list attribute with names of added (to base class) exit gates
    #       problem: need to introspect explicitly all parents with default ExitGates
    # 3. for custom Interaction class descriptor set list of attributes with type ExitGate
    #       problem: need to introspect attributes of the class by type to find ExitGates attributes
    #

    # list of connectable Signal objects for each named ExitGate
    # EXIT_GATES_SIGNALS = {}
    # signals are created at stage of Interaction class initialization

    meta = {
        'allow_inheritance': True
    }

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
        # get or create NewUserMessage sigsnal

        # self.slot_filled_signal = django.dispatch.dispatcher.Signal(
        #     providing_args=["user_slot_process", "results"])


    #@classmethod
    #def initialize(cls, ic, name=None, *args, **kwargs):
    #    """
    #    Interaction initialization requires:
    #    1. specify its name (And register it in the Interactions Registry)
    #    2. initilize EXIT GATES of the interaction.
    #        EXIT GATES are declared in implementation class, if not then default set of exit gates is assumed
    #        (the only: ExitGate_Ok)
    #
    #    :param ic:
    #    :param name:
    #    :param args:
    #    :param kwargs:
    #    :return:
    #    """
    #    if not name:
    #        # default name is a name of class
    #        name = cls.__name__
    #
    #    intrctn, _ = cls.get_or_create(name=name)
    #
    #    intrctn.ic = ic
    #
    #    # #########################################################################################
    #    # # Exit Gate Signals and Registry initialization
    #    intrctn.EXIT_GATES_SIGNALS = {}
    #
    #    if not hasattr(intrctn,'EXIT_GATES_NAMES_LIST'):
    #        # TODO fix to support inheritance of ExitGates!
    #        # then import default Gates :
    #        intrctn.EXIT_GATES_NAMES_LIST = cls.base_EXIT_GATES_NAMES_LIST
    #
    #    # now init signal objects for each exit gate:
    #    for each_exit_gate_name in intrctn.EXIT_GATES_NAMES_LIST:
    #        # create a signal object for each exit gate
    #        intrctn.EXIT_GATES_SIGNALS[each_exit_gate_name] = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])
    #
    #
    #    intrctn._anti_garbage_collector_callbacks_list = []
    #    # END ExitGate Signals Initialization
    #
    #    ########################################################################################
    #    intrctn.post_init_hook()
    #
    #    return intrctn


    def start(self, *args, **kwargs):
        """
        if start method called then we need to create a UserInteraction(Process) and then we may start logic
        :param args:
        :param kwargs:
        :return:
        """
        print(f"Start of Interaction: {self.__str__()}")
        from components.user_processes.user_interaction_process import UserInteractionProcess
        # TODO check state?
        self.user_domain = kwargs['user_domain']
        self.ic = kwargs['user_domain'].get_user_domain_controller()
        ui, _ = UserInteractionProcess.get_or_create(interaction=self,
                                                     user_domain=self.user_domain)
        return ui

    def connect_exit_gate_with_fn(self, callback_fn, exit_gate=None):
        """
        Connects Exit Gate of the interaction with callback function provided by caller

        Args:
            callback_fn:
            exit_gate: if None, then default ExitGate used

        Returns:

        """
        # import ipdb; ipdb.set_trace()

        if not exit_gate:
            # if exit gate is not provided assert that the default exit gate is used:
            exit_gate = self.EXIT_GATE_OK
        #import ipdb; ipdb.set_trace()
        print(f"connecting Exit Gate: {self} with callback function")

        # to avoid garbage collecting the functions we make hacky list:
        if not hasattr(self, "_anti_garbage_collector_callbacks_list"):
            self._anti_garbage_collector_callbacks_list = []
        self._anti_garbage_collector_callbacks_list.append(callback_fn)
        self.EXIT_GATES_SIGNAL_PATTERNS[exit_gate].connect(callback_fn, weak=False)

    def post_init_hook(self):
        """
        This is hook which allows us to overload initilization procedures, for example connect global receptors
        to dialog context
        :return:
        """
        # implement it in child class
        pass

    def __str__(self):

        if not isinstance(self.name, str):
            return self.__class__.__name__
            # print(self.name)
            # import ipdb; ipdb.set_trace()

        return self.name

