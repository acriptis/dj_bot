from components.user_domains.models import UserDomain


class AgentSkillEmulator():
    """
    Agent that initializes skills of Ruler Dialog System.

    This Agent behaves like skill so it can emulate self as aggreagted skill for DeepPavlov system.

    Agent of DeepPavlov should use __call__ method of the AgentSkillInitilizer and receive responses
    in format with confidence.

    """
    def __init__(self, skills_spec):
        """
        initialize Agent which can process requests from different Users

        Args:
            skills_spec: list of Skill classes to be initilized in Agent
        """
        self.skills_spec = skills_spec

        self.skills = []

        # phrase agent responds when there is no skill answers:
        self.dontknowphrase = "Даже не знаю что Вам ответить..."

        for each_skill_spec in self.skills_spec:
            # intilize skills
            self.skills.append(each_skill_spec())

    def __call__(self, utterance_str, user_id, *args, **kwargs):
        """
        Framework enterpoint

        :param utterance: what user said
        :param args:
        :param kwargs:
        :return:
        """
        return self.process_step(utterance_str, user_id)

    def process_step(self, utterance_str, user_id, *args, **kwargs):
        """
        Interface method for processing messages by dialog subsystem in "raw format":

        Args:
            utterance_str: str: string with user's utterance
            user_id: identifier of user
            *args:
            **kwargs:

        Returns:

        """
        print("AgentSkillEmulator.Process_step!")
        #####################################################################################
        #restore or create UserDomain
        user_domain, is_created = UserDomain.get_or_create_user_domain(user_id)

        # drop active question (asked by system) because new User message came:
        # user_domain.udm.DialogPlanner.current_step_active_question = None
        user_domain.agenda.current_step_active_question = None
        user_domain.agenda.save()
        ############################################################################
        utterance = utterance_str.strip()
        # dialog model update
        # push new message into dialog model trigger signal system with UserMessageSignal
        user_domain.udm.userdialog._push_dialog_act(user_domain.get_target_user(), utterance)
        # # ###############################################################################
        user_domain.save()
        # import ipdb; ipdb.set_trace()

        for each_skill in self.skills:
            # init interactions and receptors for newbie user
            each_skill.connect_to_dataflow(user_domain.udm)
            # now all receptors in the scenario are attached to DataFlow
        ######################################################################################
        user_domain.user_message_signal.send(sender=self, text=utterance, user_domain=user_domain)

        #########################################################################################
        # ####### Process agenda tasks #######################
        user_domain.reload()
        user_domain.udm.DialogPlanner.process_agenda()
        user_domain.reload()
        #########################################################################################
        #########################################################################################
        ###### POST PROCESSING ##########################################################################
        #########################################################################################
        # ####### Merge outputed utterances to adapt for descrete system #######################
        # we wrap responses into confidence format
        # interactions push their hypotheses with Dialog Planner
        merged_answer = ""
        if hasattr(user_domain, 'pending_utterances'):
            pending_utterances = user_domain.pending_utterances

            if len(pending_utterances)==0:
                # null response
                merged_answer = self.dontknowphrase
                pass
            elif len(pending_utterances)==1:
                # happy case
                merged_answer= pending_utterances[0]
                pass

            elif len(pending_utterances) > 1:
                # multianswer case, we need to merge messages to map with DeepPavlov
                # discrete architecture
                merged_answer = "\n".join(pending_utterances)
            # wrap it with confidence which is always constant for rule based skill:
            CONFIDENCE = 0.75
            # all utterances commited to output
            user_domain.pending_utterances = []
            # save model into persistent storage
            user_domain.save()
            # №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№

            if len(merged_answer) > 0:
                # bot answered something

                # response for the state is utterance+confidence. We mark confidence as 0.75
                state_resp = {'text': merged_answer, 'confidence': 0.75}
            else:
                state_resp = {'text': "Даже не знаю, что ответить...", 'confidence': 0.25}

            personal_info_dict = self.slots_serialization(user_domain)
            if personal_info_dict:
                state_resp.update(personal_info_dict)
            return state_resp

        else:
            print("NO PENDING UTTERANCES ATTR found")
            raise Exception("No pending utterances attribute!")
            # import ipdb; ipdb.set_trace()
            # state_resp = {}
            # return (merged_answer, 1.0 , None)

    def conjugate_autouser_with_agent(self, user_messages_sequence, user_id):
        """

            Iteratively Emulates sending messsages of the User to the Dialog System implemented
            by agent instance.

            Messages are sent step by step (as interaction with agent in discrete dialog system)

            Notes:
                Method for testing of the scenarios.

            Args:
                agent: Agent instance
                user_messages_sequence: Sequence of Messages that user must send to the agent

            Returns:
                UserDialog with results of communication

        """
        user_domain, is_created = UserDomain.get_or_create_user_domain(user_id)

        for utterance_str in user_messages_sequence:
            print(">>>" * 30)
            user_domain.udm.userdialog.print_dialog()
            print("New Message: %s" % utterance_str)
            print("VVV" * 45)
            response = self(utterance_str, user_id)

            user_domain.udm.userdialog.send_message_to_user(response['text'])
            print("Response Message: %s" % response['text'])
            # print(, flush=True)

            print("^^^" * 30)

        print("=" * 80)
        print("Final Dialog Content:")
        user_domain.udm.userdialog.print_dialog()
        return user_domain.udm.userdialog

    def slots_serialization(self, user_domain):
        """
        Serializes internal slots into AgentState API
        # https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.85j9g7xx30oo
        Returns:

        """
        # TODO refactor me
        # entail slots from internal representation into AgentState API
        # https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.85j9g7xx30oo
        # import ipdb; ipdb.set_trace()

        username_slot_value = user_domain.udm.MemoryManager.get_slot_value_quite('username_slot')
        personal_info_dict = {}
        if username_slot_value:
            personal_info_dict['name'] = username_slot_value

        interests_slot_value = user_domain.udm.MemoryManager.get_slot_value_quite('interests_slot')
        if interests_slot_value:
            personal_info_dict['interests'] = interests_slot_value

        return personal_info_dict

