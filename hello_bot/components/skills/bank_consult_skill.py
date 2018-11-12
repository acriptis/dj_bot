from components.skills.base_skill import AbstractSkill
from components.information_controller import InformationController
# from hello_bot.components.skills.base_skill import AbstractSkill, InformationController
from interactions.models import QuestionInteractionFactory, UserDialog
import django.dispatch

from interactions.models.user_slot_process import UserSlotProcess

from bank_interactions.models import DocumentsListSupplyInteraction, IntentRetrievalInteraction, \
    DesiredCurrencyInteraction, BusinessOfferingInteraction
from bank_interactions.models.greeting import GreetingInteraction
from bank_interactions.models.interactions import DesiredCurrencyInteraction


class Scenario():
    """
    Class for specification of Dialog's Scenario
    """

    def __init__(self, ic):

        self.ic = ic

        # 0. interaction for greeting
        self.greet_intrctn = GreetingInteraction.initialize(ic=ic)

        # 1.
        self.intent_clarificator = IntentRetrievalInteraction.initialize(ic=ic)
        # TODO intent clarificator internally calls DesiredCurrencyInteraction and

        # connect greeting with intent clarificator
        self.greet_intrctn.connect_exit_gate_with_fn(self.intent_clarificator.start)

        # 2.
        self.desired_currency_interaction = DesiredCurrencyInteraction.initialize(ic=ic)
        self.intent_clarificator.connect_exit_gate_with_fn(self.desired_currency_interaction.start)

        # 3.
        self.doc_list_supply_interaction = DocumentsListSupplyInteraction.initialize(ic=ic)
        self.desired_currency_interaction.connect_exit_gate_with_fn(self.doc_list_supply_interaction.start)

        import ipdb; ipdb.set_trace()

        # # 4.BusinessOfferingInteraction
        # self.business_offering_interaction = BusinessOfferingInteraction.initialize(ic=ic)
        # self.doc_list_supply_interaction.connect_exit_gate_with_fn(
        #     exit_gate=self.doc_list_supply_interaction.EXIT_GATE_3_1, callback_fn=self.business_offering_interaction.start)
        # self.desired_currency_interaction.connect_exit_gate_with_fn(self.doc_list_supply_interaction.start)


class BankConsulterAgentSkill(AbstractSkill):
    """
        Agent that is a skill as well
    """
    # signal emmitted when user message comes:
    # user_message_signal = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])

    def __init__(self, ic=None):
        # TODO implement user model
        self.user = 'Греф'

        # #############################################
        # information controller injection hack
        if not ic:
            # create information controller
            ic = InformationController(user=self.user)
        self.ic = ic
        # END ############################################

        ########################################################################################
        ####################### init scenario map ############################################
        # create user dialog and push the message
        self.userdialog = UserDialog.objects.create()

        # store userdialog in information controller
        self.ic.userdialog = self.userdialog

        # set up scenario of dialog:
        self.ic.scenario = Scenario(self.ic)

        # whom we ask to start SlotInteraction?

        # pending goals
        # self.goals = [curr_slot_spec]


        # END load scenario map ############################################

        # start dialog by
        # 1. greeting (GreetInteraction) and
        # 2. asking user question about intent (IntentClarificator)


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

        # now we have dialog and utterance preloaded

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

        # TODO show pending receptors


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
            ########################### Check Pending Interactions Plan ##############################################
            # Alternative else scenario:
            # check if we have queue of actions in plan
            print("self.ic.DialogPlanner.queue")


            print(self.ic.DialogPlanner.queue)
            if len(self.ic.DialogPlanner.queue)>0:
                # import ipdb;
                # ipdb.set_trace()
                self.ic.DialogPlanner.launch_next_task()
            else:
                # nothing to say, nothing to do...
                #TODO templatize
                self.userdialog.send_message_to_user("Sorry, I don't understand your blah blah blah")
        # responses = ["kek %s" % text for text in utterances_batch]
        # confidences = [0.5 for x in range(len(utterances_batch))]
        return responses_list


# ############################################################################################################
# ##################################### Trashy Code Snippets #####################################
class AbstractRuleSwitch():
    def check(self, context):
        """

        :param context:
        :return: bool
        """
        pass

    def action(self, context):
        """
        Actualization of RuleConsequence

        Action may:
            emit production signals in the system (for some other components)
            sendText operation
            announce termination
            route control to operator

            launch interaction (put into Goals/Agenda)
            launch SlotFillingProcess

        :param context:
        :return: ?
        """

    def else_action(self):
        """????"""
        pass


class DecisionPolicy():
    # when it called?
    # how to keep flexibility and ease of bootstrap (default policy)?

    pass
