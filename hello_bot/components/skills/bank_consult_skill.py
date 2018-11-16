from components.skills.base_skill import AbstractSkill
from components.information_controller import InformationController
# from hello_bot.components.skills.base_skill import AbstractSkill, InformationController
from interactions.models import QuestionInteractionFactory, UserDialog
import django.dispatch

from interactions.models.user_slot_process import UserSlotProcess

from bank_interactions.models import DocumentsListSupplyInteraction, IntentRetrievalInteraction, \
    BusinessOfferingInteraction, ConsideringSelfServiceInteraction
from bank_interactions.models.greeting import GreetingInteraction
from bank_interactions.models.interactions import DesiredCurrencyInteraction


class Scenario():
    """
    Class for specification of Dialog's Scenario
    """

    def __init__(self, ic):

        self.ic = ic
        # ########################################################################################
        # Initialize interaction objects:

        # 0. interaction for greeting
        self.greet_intrctn = self.ic.im.get_or_create_instance_by_class(GreetingInteraction)
        # old approach:
        # self.greet_intrctn = GreetingInteraction.initialize(ic=ic)

        # 1. intent
        self.intent_clarificator = self.ic.im.get_or_create_instance_by_class(IntentRetrievalInteraction)
        # self.intent_clarificator = IntentRetrievalInteraction.initialize(ic=ic)

        # TODO intent clarificator internally calls DesiredCurrencyInteraction!!
        # TODO intent clarificator internally calls BusinessOfferingInteraction!!
        # 2. desired currency
        self.desired_currency_interaction = self.ic.im.get_or_create_instance_by_class(DesiredCurrencyInteraction)
        # self.desired_currency_interaction = DesiredCurrencyInteraction.initialize(ic=ic)

        # 3.
        self.doc_list_supply_interaction = self.ic.im.get_or_create_instance_by_class(DocumentsListSupplyInteraction)
        # self.doc_list_supply_interaction = DocumentsListSupplyInteraction.initialize(ic=ic)

        # 4.BusinessOfferingInteraction
        self.business_offering_interaction = self.ic.im.get_or_create_instance_by_class(BusinessOfferingInteraction)
        # self.business_offering_interaction = BusinessOfferingInteraction.initialize(ic=ic)

        # 5.
        self.consideringselfserviceinteraction = self.ic.im.get_or_create_instance_by_class(ConsideringSelfServiceInteraction)
        # END Initialize interaction objects:
        # ########################################################################################


        # ########################################################################################
        # Specify linking between interaction ExitGates:

        # connect greeting with intent clarificator
        self.greet_intrctn.connect_exit_gate_with_fn(
            callback_fn=self.intent_clarificator.start)

        # intent clarification with desired_currency_interaction
        # comment it if intent_clarificator internally calls the desired currency interaction:
        # self.intent_clarificator.connect_exit_gate_with_fn(
        #     callback_fn=self.desired_currency_interaction.start)

        self.desired_currency_interaction.connect_exit_gate_with_fn(
            callback_fn=self.doc_list_supply_interaction.start)

        # import ipdb; ipdb.set_trace()


        self.doc_list_supply_interaction.connect_exit_gate_with_fn(
            exit_gate=self.doc_list_supply_interaction.EXIT_GATE_3_1,
            callback_fn=self.business_offering_interaction.start)

        self.business_offering_interaction.connect_exit_gate_with_fn(
            callback_fn=self.consideringselfserviceinteraction.start)

        # import ipdb; ipdb.set_trace()
        # print("lkk")
        # END Specify linking between interaction ExitGates:
        # ########################################################################################

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
            print("no interactions have responded to the latest utterance...")
            # no responses from system:
            # else scenario
            ########################### Check Pending Interactions Plan ##############################################
            # Alternative else scenario:
            # check if we have queue of actions in plan
            print("self.ic.DialogPlanner.agenda.queue_of_tasks")
            print(self.ic.DialogPlanner.agenda.queue_of_tasks)
            if len(self.ic.DialogPlanner.agenda.queue_of_tasks)>0:
                # import ipdb;
                # ipdb.set_trace()
                self.ic.DialogPlanner.launch_next_task()
            else:
                # nothing to say, nothing to do...
                #TODO templatize
                self.userdialog.send_message_to_user("Простите, я не знаю, что Вам ответить ;)")
        # responses = ["kek %s" % text for text in utterances_batch]
        # confidences = [0.5 for x in range(len(utterances_batch))]
        return responses_list

