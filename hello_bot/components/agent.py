from components.information_controller import InformationController
from bank_bot.settings import DEFAULT_USER_NAME

class AgentSkillInitializer():
    """
    Agent that initializes skills.
    This Agent works only as personal Agent (means for each User we need to create a new Agent
    instance and keep it alive until dialog ends, otherwise connections between actions will be
    forgotten by Agent...).

    Problem of persistency and better multiuser support will be implemented in ruler_bot framework.
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

        Args:
            utterance: what user said
            *args:
            **kwargs:

        Returns:

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

        self.ic.DialogPlanner.process_agenda()

        responses_list = self.ic.userdialog.show_latest_sys_responses()

        # merge utterances for discrete Dialog System
        bot_resp = ". ".join(responses_list)

        if len(bot_resp)>0:
            # bot answered something

            # response for the state is utterance+confidence. We mark confidence as 0.75
            state_resp = {'text': bot_resp, 'confidence': 0.75}
        else:
            state_resp = {'text': "Даже не знаю, что ответить...", 'confidence': 0.25}

        personal_info_dict = self.slots_serialization()
        if personal_info_dict:
            state_resp.update(personal_info_dict)
        return state_resp

    def slots_serialization(self):
        """
        Serializes internal slots into AgentState API
        # https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.85j9g7xx30oo
        Returns:

        """
        # TODO refactor me
        # entail slots from internal representation into AgentState API
        # https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.85j9g7xx30oo
        username_slot_value = self.ic.MemoryManager.get_slot_value_quite('username_slot')
        personal_info_dict = {}
        if username_slot_value:
            personal_info_dict['name'] = username_slot_value

        interests_slot_value = self.ic.MemoryManager.get_slot_value_quite('interests_slot')
        if interests_slot_value:
            personal_info_dict['interests'] = interests_slot_value

        return personal_info_dict