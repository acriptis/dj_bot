from components.skills.base_skill import AbstractSkill
from components.information_controller import InformationController
# from hello_bot.components.skills.base_skill import AbstractSkill, InformationController
from interactions.models import QuestionInteractionFactory, UserDialog
import django.dispatch

from interactions.models.user_slot_process import UserSlotProcess

from bank_interactions.models import DocumentsListSupplyInteraction, IntentRetrievalInteraction, \
    BusinessOfferingInteraction, ConsideringSelfServiceInteraction, OnlineReservingFinalizationInteraction, \
    OfficeRecommendationInteraction, DialogTerminationInteraction, OperatorSwitchInteraction
from bank_interactions.models.greeting import GreetingInteraction
from bank_interactions.models.interactions import DesiredCurrencyInteraction
from personal_assistant_skills.models import WeatherForecastInteraction, AlarmSetterInteraction


class Scenario():
    """
    Class for specification of Dialog's Scenario
    """
    # TODO do we need AbstractScenario?
    def __init__(self, ic):

        self.ic = ic
        # ########################################################################################
        # Initialize interaction objects:

        # 0. interaction for greeting
        self.greet_intrctn = self.ic.im.get_or_create_instance_by_class(GreetingInteraction)
        # old approach:
        # self.greet_intrctn = GreetingInteraction.initialize(ic=ic)

        # 1. intent
        self.s1_intent_clarificator = self.ic.im.get_or_create_instance_by_class(IntentRetrievalInteraction)
        # self.intent_clarificator = IntentRetrievalInteraction.initialize(ic=ic)

        # TODO intent clarificator internally calls DesiredCurrencyInteraction!!
        # TODO intent clarificator internally calls BusinessOfferingInteraction!!
        # 2. desired currency
        self.s2_desired_currency_interaction = self.ic.im.get_or_create_instance_by_class(DesiredCurrencyInteraction)
        # self.desired_currency_interaction = DesiredCurrencyInteraction.initialize(ic=ic)

        # 3.
        self.s3_doc_list_supply_interaction = self.ic.im.get_or_create_instance_by_class(DocumentsListSupplyInteraction)
        # self.doc_list_supply_interaction = DocumentsListSupplyInteraction.initialize(ic=ic)

        # 4.BusinessOfferingInteraction
        self.s4_business_offering_interaction = self.ic.im.get_or_create_instance_by_class(BusinessOfferingInteraction)
        # self.business_offering_interaction = BusinessOfferingInteraction.initialize(ic=ic)

        # 5.
        self.s5_considering_self_service_interaction = self.ic.im.get_or_create_instance_by_class(ConsideringSelfServiceInteraction)

        # 6.
        self.s6_online_reserving_finalization_interaction = self.ic.im.get_or_create_instance_by_class(OnlineReservingFinalizationInteraction)

        # 7.
        self.s7_office_recommendation_interaction = self.ic.im.get_or_create_instance_by_class(OfficeRecommendationInteraction)

        # 8. Termination of dialog
        self.s8_dialog_termination_interaction = self.ic.im.get_or_create_instance_by_class(DialogTerminationInteraction)

        # 9. Operator Switch
        self.s9_operator_switch_interaction = self.ic.im.get_or_create_instance_by_class(OperatorSwitchInteraction)
        # END Initialize interaction objects:
        # ########################################################################################


        # ########################################################################################
        # Specify linking between interaction ExitGates:

        # connect greeting with intent clarificator
        self.greet_intrctn.connect_exit_gate_with_fn(
            callback_fn=self.s1_intent_clarificator.start)

        # intent clarification with desired_currency_interaction
        # comment it if intent_clarificator internally calls the desired currency interaction:
        # self.intent_clarificator.connect_exit_gate_with_fn(
        #     callback_fn=self.desired_currency_interaction.start)

        self.s2_desired_currency_interaction.connect_exit_gate_with_fn(
            callback_fn=self.s3_doc_list_supply_interaction.start)

        # import ipdb; ipdb.set_trace()
        # TODO add priorities support
        # TODO unify interface of scenario planning with Agenda
        # 3.EXIT_GATE_3_1 -> 4.start
        self.s3_doc_list_supply_interaction.connect_exit_gate_with_fn(
            exit_gate=self.s3_doc_list_supply_interaction.EXIT_GATE_3_1,
            callback_fn=self.s4_business_offering_interaction.start)

        # ExitGate3.2.RUB -> 6.start
        self.s3_doc_list_supply_interaction.connect_exit_gate_with_fn(
            exit_gate=self.s3_doc_list_supply_interaction.EXIT_GATE_3_2_RUB,
            callback_fn=self.s6_online_reserving_finalization_interaction.start)
        # ExitGate3.2.NonRUB -> 7.start
        # TODO add prioritization into connections
        self.s3_doc_list_supply_interaction.connect_exit_gate_with_fn(
            exit_gate=self.s3_doc_list_supply_interaction.EXIT_GATE_3_2_NONRUB,
            callback_fn=self.s7_office_recommendation_interaction.start)


        # 4.Exit -> 5.start
        self.s4_business_offering_interaction.connect_exit_gate_with_fn(
            callback_fn=self.s5_considering_self_service_interaction.start)

        # 5.Exit -> 6.start
        self.s5_considering_self_service_interaction.connect_exit_gate_with_fn(
            callback_fn=self.s6_online_reserving_finalization_interaction.start)

        # 6 Exits: ###########################################
        # 6.ExitGate_6_NONRUB_RESERVATION_OFFLINE -> 7.start
        self.s6_online_reserving_finalization_interaction.connect_exit_gate_with_fn(
            exit_gate=self.s6_online_reserving_finalization_interaction.EXIT_GATE_6_NONRUB_RESERVATION_OFFLINE,
            callback_fn=self.s7_office_recommendation_interaction.start)
        # 6.EXIT_GATE_6_RUB_READY -> 9.start
        self.s6_online_reserving_finalization_interaction.connect_exit_gate_with_fn(
            exit_gate=self.s6_online_reserving_finalization_interaction.EXIT_GATE_6_RUB_READY,
            callback_fn=self.s9_operator_switch_interaction.start)
        # 6.EXIT_GATE_6_RUB_UNREADY -> 8.start
        self.s6_online_reserving_finalization_interaction.connect_exit_gate_with_fn(
            exit_gate=self.s6_online_reserving_finalization_interaction.EXIT_GATE_6_RUB_UNREADY,
            callback_fn=self.s8_dialog_termination_interaction.start)
        #####################################################

        # 7.Exit -> 8.start
        self.s7_office_recommendation_interaction.connect_exit_gate_with_fn(
            callback_fn=self.s8_dialog_termination_interaction.start)

        # import ipdb; ipdb.set_trace()
        # print("lkk")
        # END Specify linking between interaction ExitGates:
        # ########################################################################################


class AgentSkillInitializer():
    """
    Agent that initializes skills
    Instead of basic agent which requires skills
    """
    def __init__(self, skills_spec):
        self.skills_spec = skills_spec

        self.skills = []

        # Agent Customization:
        # TODO implement user model
        self.user = 'Иван Павлов'

        # create information controller
        self.ic = InformationController(user=self.user)

        # # create user dialog and push the message
        # self.userdialog = UserDialog.objects.create()
        # # store userdialog in information controller
        # self.ic.userdialog = self.userdialog

        for each_skill_cls in self.skills_spec:
            # initialize skills that expect information controller access
            self.skills.append(each_skill_cls(self.ic))

    def __call__(self, utterance, *args, **kwargs):
        """
        Framework enterpoint
        :param utterance: what user said
        :param args:
        :param kwargs:
        :return:
        """
        # push user's utterance into userdialog container
        utterance = utterance.strip()
        self.ic.userdialog._push_dialog_act(self.user, utterance)
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

        # polling listeners (receptors/skills) with new message:
        self.ic.user_message_signal.send(sender=self, message=utterance, userdialog=self.ic.userdialog)

        # TODO show pending receptors

        self.ic.DialogPlanner.process_agenda()

        responses_list = self.ic.userdialog.show_latest_sys_responses()

        return responses_list

# TODO clarify where to place IC in case of MultipleSkills!
# answer: must be shared by agent
# if so then skills must initilize IC or get existing singleton!

class BankConsulterSkill(AbstractSkill):
    """
        Skill for bank consulting
    """

    def __init__(self, ic):
        self.ic = ic
        # set up scenario of dialog:
        self.ic.scenario = Scenario(self.ic)
