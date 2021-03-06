from deeppavlov.core.models.component import Component
from interactions.models import GreetInteraction, ByeInteraction
from interactions.models import QuestionInteractionFactory, UserDialog
from components.information_controller import InformationController


class AbstractSkill(Component):
    def __call__(self, utterances_batch, history_batch, states_batch,*args, **kwargs) -> (str, float):
        """
        main call method each skill should respond with answer as str and confidence tuple
        :param utterances_batch:
        :param history_batch:
        :param states_batch:
        :return:
        """
        pass

# #########################################################################################
# interactions

class MonopolyAgentSkill(AbstractSkill):
    """
        Agent that is a skill as well
    """
    # signal emmitted when user message comes:
    # user_message_signal = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])

    def __init__(self, ic=None):
        # #############################################
        # information controller injection hack
        if not ic:
            # create information controller
            ic = InformationController()
        self.ic = ic

        # TODO implement user model
        self.user = 'Gennadiy'
        # END ############################################

        ########################################################################################
        ####################### init scenario map ############################################
        # create user dialog and push the message
        self.userdialog = UserDialog.objects.create()

        # store userdialog in information controller
        self.ic.userdialog = self.userdialog

        # interaction for greeting
        self.greet_intrctn, created = GreetInteraction.objects.get_or_create()
        self.farewell_intrctn, created = ByeInteraction.objects.get_or_create()

        # TODO templatize question
        self.what_is_ur_name_intrctn, _ = QuestionInteractionFactory.objects.get_or_create(question="What is your name?", slot_name="user_name")

        # connecting interactions to informationController
        # interaction connects itself to global receptors
        self.greet_intrctn.post_init_hook()
        self.farewell_intrctn.post_init_hook()
        self.what_is_ur_name_intrctn.post_init_hook()
        self.greet_intrctn.connect_exit_gate_with_fn(self.what_is_ur_name_intrctn.start)
        self.what_is_ur_name_intrctn.connect_exit_gate_with_fn(self.farewell_intrctn.start)

        # END load scenario map ############################################


    def __call__(self, utterance, *args, **kwargs):
        """
        Framework enterpoint
        :param utterance: what user said
        :param args:
        :param kwargs:
        :return:
        """
        # push last utterance into userdialog stracture
        utterance = utterance.strip()
        self.userdialog._push_dialog_act(self.user, utterance)
        ############################################################################

        ################################################################################
        ## QUD: Question on Discussion handling attempt #########################
        # first try to handle answer as response for questions under discussion:
        # for each_question in self.userdialog.questions_under_discussion:
        #     print(each_question)
        # else:
        #     print("No questions on discussion")

        # print("Active Receptors polling")
        # active receptors is a list of
        # 1. locally active receptors from active user interactions
        # 2. globally active receptors from scenario interactions

        # polling listeners (receptors) with new message:
        self.ic.user_message_signal.send(sender=self, message=utterance, userdialog=self.userdialog)

        # for each_receptor in self.ic.active_receptors:
        #     # receptor_activated = each_receptor(utterance, self.userdialog)
        #     # print(receptor_activated)
        #     pass

        responses_list = self.userdialog.show_latest_sys_responses()
        # # exceptional case:
        if not responses_list:
            # no interactions have responded to the utterance...
            # no responses from system:
            # else scenario
            #TODO templatize
            self.userdialog.send_message_to_user("Sorry, I don't understand your blah blah blah")
        # responses = ["kek %s" % text for text in utterances_batch]
        # confidences = [0.5 for x in range(len(utterances_batch))]
        return responses_list

class MonopolySkill(AbstractSkill):
    def __init__(self, ic=None):
        # #############################################
        # information controller injection hack
        if not ic:
            # create information controller
            ic = {}
        self.ic = ic
        # END ############################################

    def __call__(self, utterances_batch, history_batch, states_batch, *args, **kwargs):
        # print("VVVVVVVV")
        # print("utterances_batch")
        # print(utterances_batch)
        # print("history_batch")
        # print(history_batch)
        # print("states_batch")
        # print(states_batch)
        # print(args)
        # print(kwargs)
        # print("^^^^^^^^")
        # TODO design confidence propagation
        responses = ["kek %s" % text for text in utterances_batch]
        confidences = [0.5 for x in range(len(utterances_batch))]
        return responses, confidences

    def process(self):
        pass