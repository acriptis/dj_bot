from django.db import models
# Create your models here.
from polls.models import Question
from components.matchers.matchers import TrainigPhrasesMatcher
import django.dispatch

# just constant for system responses:
SYSTEM_USER_NAME = 'sys'

class UserDialog(models.Model):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        # each message is here:
        self.dialog_acts = []
        # parallel list with authors of each dialog act
        self.dialog_speakers = []

        self.last_message = ""

        self.memory = {}

        self.active_user_interactions = []

        # list of QuestionInteractions waiting for response
        self.questions_under_discussion = []

    def _push_dialog_act(self, author, message):
        """
        :param author:
        :param message:
        :return:
        """
        self.dialog_acts.append(message)
        self.dialog_speakers.append(author)
        self.last_message = message
        return self

    def print_dialog(self):
        zipped_messages = list(zip(self.dialog_speakers, self.dialog_acts))
        for each_author, each_message in zipped_messages:
            print("%10s: %s" % (each_author, each_message ))

    def send_message_to_user(self, message):
        """
        Interface to send messages to User (via Telegram or any other DialogBroker)
        :return: self
        """
        if not message:
            import ipdb; ipdb.set_trace()
            print("empty message?")
        return self._push_dialog_act(SYSTEM_USER_NAME, message)

    def show_latest_sys_responses(self):
        # import ipdb; ipdb.set_trace()
        # find highest non sys index:
        user_indexes = [i for i, x in enumerate(self.dialog_speakers) if x != SYSTEM_USER_NAME]
        # import ipdb; ipdb.set_trace()

        max_user_index = max(user_indexes)

        # find system responses after latest user input:
        latest_sys_indexes = [i for i, x in enumerate(self.dialog_speakers) if (x == SYSTEM_USER_NAME and i>max_user_index)]
        sys_answers = [self.dialog_acts[i] for i in latest_sys_indexes]
        return sys_answers


class AbstractInteraction():


    def __init__(self, *args, **kwargs):
        self.exit_gate_signal = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])
        # signal sent on completion? of interaction:

    def connect_exit_gate_with_fn(self, callback_fn):
        self.exit_gate_signal.connect(callback_fn)


class Interaction(models.Model):
    """
    Base ORM model for interaction specification
    """
    name = models.CharField(max_length=200)


class SendTextOperation(Interaction):
    # send to send:
    text = models.CharField(max_length=200)

    # TODO add support of templates and variables filling

    def do(self, ic=None):
        """
        Actual implementation of behaviour
        :return:
        """
        # TODO
        # then user interaction sets its state to completed
        return self.text

    # def __init__(self, text):
    #     self.text = text


class UserInteraction(models.Model):
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    # # user no user now)
    #
    INIT = 'Init'
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'
    IGNORED = 'Ignored'
    INTERACTION_STATES = (
        (INIT, 'init'),
        (ACTIVE, 'Active'),
        (IGNORED, 'Ignored'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    )

    state = models.CharField(
        max_length=2,
        choices=INTERACTION_STATES,
        default=INIT
    )

    userdialog = models.ForeignKey(UserDialog, on_delete=models.CASCADE)

    # def __init__(self, interaction, user, userdialog):
    #     self.interaction = interaction
    #     # if not status:
    #     #     status = self.INIT
    #     # self.status=status
    #
    #     # pointer to the node of latest_completed interaction of the graph:
    #     self.state_pointer=self.interaction.input_gate
    #     self.user=user
    #     self.state =
    #
    # def start_scenario_process(self, *args, **kwargs):
    #     """
    #     Input Gate is here
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     self.state = self.ACTIVE
    #     # what we return here?
    #     do_results_deferred = self.interaction.do(*args, **kwargs)
    #     # if done
    #     self.state = self.COMPLETED
    #     return do_results_deferred
    #
    # @classmethod
    # def activate(cls, interaction):
    #     uiprocess = UserInteraction(interaction=interaction,
    #                     # user=user,
    #                     state=UserInteraction.INIT
    #                     )
    #     return uiprocess
    #
    # @classmethod
    # def resume_or_init(self, interaction):
    #     # TODO
    #     pass
    #
    # def _resume(self):
    #     if self.state_pointer:
    #         # TODO multiouts?
    #         self.interaction.graph[self.state_pointer].out



#############################################################################################################
#############################################################################################################


class QuestionInteractionFactory(Interaction, AbstractInteraction):
    question = models.CharField(max_length=200)
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


    def connect_to_dataflow(self, ic):
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
            # emit signal of completion:
            self.exit_gate_signal.send(sender=self, userdialog=userdialog)
            return True
        else:
            self.ic.userdialog.send_message_to_user("So what is your name?")
            return False


#############################################################################################################
#############################################################################################################
# Domain Specific Interactions
# TODO move into sep module
class GreetInteraction(Interaction, AbstractInteraction):

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

    def connect_to_dataflow(self, ic):
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

        self.exit_gate_signal.send(sender=self.__class__, userdialog=self.ic.userdialog)

        # import ipdb; ipdb.set_trace()
        # TODO refactor:
        # TODO send signal scenario completion
        uint.state = UserInteraction.COMPLETED
        uint.save()


        return "kukuku"

    def start(self, *args, **kwargs):
        self.do(*args, **kwargs)


class ByeInteraction(Interaction, AbstractInteraction):
    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        super(AbstractInteraction, self).__init__()
        self.text = "Bye, honey!"
        self.scenario = SendTextOperation(text=self.text)
        # self.text = "Bye, honey!"

        # this Interaction may be activated by Receptor
        self.global_trigger_receptor = TrainigPhrasesMatcher(training_phrases=["Bye", "Spoki", "Tchao"],
                                                             daemon_if_matched=self.do)

    def connect_to_dataflow(self, ic):
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

# class ExceptionInteraction():
#     def do(self,  *args, **kwargs):
#         sto = SendTextOperation(text="I don't know what you mean!")
#         sto.do(self.ic)