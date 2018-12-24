from components.information_controller import InformationController
from bank_bot.settings import DEFAULT_USER_NAME

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
        # interlocutor
        from interactions.models.userdialog import DPUserProfile

        self.user = DPUserProfile.get_or_create_userprofile(DEFAULT_USER_NAME)

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

        # drop active question (asked by system) because new User message came:
        self.ic.DialogPlanner.current_step_active_question = None
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