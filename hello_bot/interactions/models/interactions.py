
from django.db import models
import django.dispatch

from interactions.models.exit_gates import ExitGate


class AbstractInteraction():
    """
    Specification of Interaction That announces its exit to those who may be concerned

    Signal is available after initialization...
    """

    # Exit Gates Default Speicification:
    EXIT_GATE_OK = "ExitGate_Ok"

    base_EXIT_GATES_NAMES_LIST = [
        EXIT_GATE_OK
    ]

    @classmethod
    def get_name(cls):
        return cls.__name__

    def start(self, *args, **kwargs):
        raise Exception("NotImplemented")


class Interaction(models.Model):
    """
    Base ORM model for interaction specification
    """
    name = models.CharField(max_length=200)

    EXIT_GATE_OK = "ExitGate_Ok"

    ##################################################################
    # Exit Gates declaration:
    # default_exit_gate = ExitGate(EXIT_GATE_OK)

    #
    base_EXIT_GATES_NAMES_LIST = [
        EXIT_GATE_OK
    ]
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

        intrctn, _ = cls.objects.get_or_create(name=name)

        intrctn.ic = ic

        # #########################################################################################
        # # Exit Gate Signals and Registry initialization
        intrctn.EXIT_GATES_SIGNALS = {}

        if not hasattr(intrctn,'EXIT_GATES_NAMES_LIST'):
            # TODO fix to support inheritance of ExitGates!
            # then import default Gates :
            intrctn.EXIT_GATES_NAMES_LIST = cls.base_EXIT_GATES_NAMES_LIST

        # now init signal objects for each exit gate:
        for each_exit_gate_name in intrctn.EXIT_GATES_NAMES_LIST:
            # create a signal object for each exit gate
            intrctn.EXIT_GATES_SIGNALS[each_exit_gate_name] = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])


        intrctn._anti_garbage_collector_callbacks_list = []
        # END ExitGate Signals Initialization

        ########################################################################################
        intrctn.post_init_hook()

        return intrctn

    def start(self, *args, **kwargs):
        """
        if start method called then we need to create a UserInteraction(Process) and then we may start logic
        :param args:
        :param kwargs:
        :return:
        """
        print("Start of Interaction: %s" % self)
        from interactions.models import UserInteraction
        # TODO check state?
        ui, _ = UserInteraction.objects.get_or_create(interaction=self, userdialog=self.ic.userdialog)
        return ui

    def connect_exit_gate_with_fn(self, callback_fn, exit_gate=None):
        if not exit_gate:
            # if exit gate is not provided assert that the default exit gate is used:
            exit_gate = self.EXIT_GATE_OK
        print("connecting Exit Gate: %s, cb_fn: %s" % (self, callback_fn))
        # self.exit_gate_signal.connect(callback_fn)
        # import ipdb; ipdb.set_trace()

        # to avoid garbage collecting the functions we make hacky list:
        # self.ic.DialogPlanner._callbacks_storage.append(callback_fn)
        self._anti_garbage_collector_callbacks_list.append(callback_fn)
        self.EXIT_GATES_SIGNALS[exit_gate].connect(callback_fn)

    def post_init_hook(self):
        """
        This is hook which allows us to overload initilization procedures, for example connect global receptors
        to dialog context
        :return:
        """
        # implement it in child class
        pass

    def __str__(self):
        return self.name


class QuestionInteractionFactory(Interaction, AbstractInteraction):
    # TODO allow generative template (GenericField)
    question = models.CharField(max_length=200)

    # URI?
    slot_name = models.CharField(max_length=200)

    # TODO generate random signal id per object?
    # random seq for signal differentiation
    dispatch_id = "dkjfbhdsfkj"
    # def __init__(self, question, slot_name, *args, **kwargs):
    #
    #     self.question=question
    #     self.slot_name = slot_name
    #     self.input_gate = "input_gate"
    #
    #     # TODO multiple output gates?
    #     self.exit_gate = "exit_gate"
    #
    #     self.question_obj = SendTextOperation(question)
    #
    #     if receptor_fn:
    #         self.response_receptor = receptor_fn
    #     self.user_wait_op = WaitUserResponseOperation()
    #     # self.receptor=receptor
    #
    #     # G = nx.DiGraph()
    #     # # InputGate -> QuestionObj -> (UserWaitOp -> ResponseReceptor) -> ?MultiGateRouter? -> ExitGate
    #     # G.add_node(self.input_gate)
    #     # G.add_node(self.question_obj)
    #     # G.add_edge(self.input_gate, self.question_obj, object="then")
    #     #
    #     # G.add_node(self.user_wait_op)
    #     # G.add_edge(self.question_obj, self.user_wait_op, object="then")
    #     #
    #     # G.add_node(self.response_receptor)
    #     # G.add_edge(self.user_wait_op, self.response_receptor, object="then")
    #     #
    #     # self.scenario_graph = G

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        super(AbstractInteraction, self).__init__()

    def post_init_hook(self, ic):
        """
        here we connect the interaction's Global Receptors with InformationController
        :return:
        """

        self.ic = ic

    def start(self, *args, **kwargs):
        # entrance point for interaction
        # 1. make userInteraction if it is not exist
        # 2. make actions until userWait or makeActions and Complete user interaction
        # print("kekeke")
        # print(args)
        # print(kwargs)

        print("START")
        self.active_user_interaction = UserInteraction.objects.get_or_create(interaction=self, userdialog=kwargs['userdialog'], state=UserInteraction.ACTIVE)
        self.ask_question(kwargs['userdialog'])
        # self.ic.user_message_signal.connect(self.response_receptor)
        # self.ic.active_receptors.append(self.response_receptor)
        # import ipdb; ipdb.set_trace()
        # print(active_interaction)

    def ask_question(self, userdialog):
        # send text operation
        userdialog.send_message_to_user(self.question)
        self.ic.user_message_signal.connect(self.response_receptor, dispatch_uid=self.dispatch_id)
        # now we must attach self for listening further responses or the next one


        # userdialog.signals["UserMessage"].connect(self.response_receptor)
        # userdialog.agenda.append(self)

    def response_receptor(self, message, userdialog, *args, **kwargs):
        """
        aka check match
        :param userdialog:
        :param message:
        :return: False if not recepted
        True if ok
        """
        # TODO make message validation
        # validated
        # import ipdb; ipdb.set_trace()
        result = self.ic.user_message_signal.disconnect(self.response_receptor, dispatch_uid=self.dispatch_id)
        if result:
            # disconnected
            print("disconnected")
        else:
            # some shit
            import ipdb;
            ipdb.set_trace()

            print("NOT disconnected")

        print("response receptor of QuestionAnswerer")

        def percept_matched_message(message, *args):
            """
            Dummy extractor
            this method extracts values from message (while check match just checks if it matched)
            :param message:
            :param args:
            :return:
            """
            extraction = {self.slot_name: message}
            return extraction

        def check_match(message):
            if len(message)>=2:

                return True
            else:
                return False

        if check_match(message):

            # send signal with data (for asyncronous handling by those who may be concerned about perception)
            # and return True for caller arbiter?
            extract = percept_matched_message(message)
            userdialog.memory = extract[self.slot_name]
            print("extracted the value: %s" % extract)
            # disconnect response listener:

            # import ipdb; ipdb.set_trace()

            self.ic.userdialog.send_message_to_user("Nice to know you %s" % extract[self.slot_name])
            import ipdb; ipdb.set_trace()
            # TODO unworking part:
            # emit signal of completion:
            # self.exit_gate_signal.send(sender=self, userdialog=userdialog)
            # # TODO migrate to:
            # self.EXIT_GATES_SIGNALS[exit_gate].send(sender=self, userdialog=self.ic.userdialog)
            return True
        else:
            self.ic.userdialog.send_message_to_user("So what is your name?")
            return False



#############################################################################################################
#############################################################################################################
# Domain Specific Interactions
# TODO move into sep module
class GreetInteraction(Interaction, AbstractInteraction):

    class Meta:
        proxy = True
    # exit_gate_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        super(AbstractInteraction, self).__init__()
        # super(AbstractInteraction, self).__init__()
        self.out_text = "Hello, dear!"
        self.scenario = SendTextOperation(text=self.out_text)
        # this Interaction may be activated by Receptor
        self.global_trigger_receptor = TrainigPhrasesMatcher(training_phrases=["Hello", "Kek", "Hi"],
                                                             daemon_if_matched=self.do)

    def post_init_hook(self, ic):
        """
        here we connect the interaction's Global Receptors with InformationController
        :return:
        """

        self.ic = ic

        # self.exit_gate_signal = django.dispatch.Signal(providing_args=["userdialog"])
        ic.user_message_signal.connect(self.global_trigger_receptor)
        # ic.active_receptors.append(self.global_trigger_receptor)

    def do(self, *args, **kwargs):
        """
        What happens just after activation
        :return:
        """
        uint, created = UserInteraction.objects.get_or_create(userdialog=self.ic.userdialog, interaction=self)

        print("hi_interaction.do")
        # actually send to chat
        # TODO make hypotheses queues?
        self.ic.userdialog.send_message_to_user(self.out_text)

        # self.exit_gate_signal.send(sender=self.__class__, userdialog=self.ic.userdialog)
        self.EXIT_GATES_SIGNALS[self.EXIT_GATE_OK].send(sender=self, userdialog=self.ic.userdialog)
        # import ipdb; ipdb.set_trace()
        # TODO refactor:
        # TODO send signal scenario completion
        uint.state = UserInteraction.COMPLETED
        uint.save()


        return "kukuku"

    def start(self, *args, **kwargs):
        self.do(*args, **kwargs)


class ByeInteraction(Interaction, AbstractInteraction):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        super(AbstractInteraction, self).__init__()
        self.text = "Bye, honey!"
        self.scenario = SendTextOperation(text=self.text)
        # self.text = "Bye, honey!"

        # this Interaction may be activated by Receptor
        self.global_trigger_receptor = TrainigPhrasesMatcher(training_phrases=["Bye", "Spoki", "Tchao"],
                                                             daemon_if_matched=self.do)

    def post_init_hook(self, ic):
        """
        here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        # ic.receptors
        self.ic = ic
        ic.user_message_signal.connect(self.global_trigger_receptor)
        # ic.active_receptors.append(self.global_trigger_receptor)

    def do(self, *args, **kwargs):
        """
        What happens just after activation
        :return:
        """
        print("bye_interaction.do")
        self.ic.userdialog.send_message_to_user(self.text)

        # 1. create user interaction state machine
        # 2. activate user interaction
        # 3.
        return "kuku"

    def start(self, *args, **kwargs):

        self.do(*args, **kwargs)


# TODO:
class FormFillingInteraction():
    """
    # TODO make Factory abstraction!
    FormValidation in Django:
    https://docs.djangoproject.com/en/2.1/ref/forms/validation/#validating-fields-with-clean
    """
    pass

    def start(self):
        pass

    def _get_form_slots(self):
        """
        Abstract method for receiving list of all slots
        :return:
        """
        pass
