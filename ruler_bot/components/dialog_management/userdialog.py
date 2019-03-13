# from components.deep_pavlov_agent_state.models import Utterance


class UserDialog():
    """
    Dialog Proxy model for interactions between System and User (2 participants)

    Uses Dialog Data Model
    """

    def __init__(self, dialog, *args, **kwargs):
        #super().__init__(*args, **kwargs)

        self.dialog = dialog
        # self.target_user =
        self.last_message = ""

    def _push_dialog_act(self, author, message):
        """
        The method to put the message from some author:User into persistent dialog model
        :param author:
        :param message:
        :return:
        """
        self.last_message = message
        return self.dialog._push_dialog_act(author, message)

    def serialize_dialog_dirty(self):
        """
        Console Friendly and Human Readable dialog representation

        :return: output_str - formatted string with names, turn numbers and message texts
        """

        output_str = ""
        # zipped_messages = list(zip(self.dialog_speakers, self.dialog_acts))
        counter = 0
        #import ipdb; ipdb.set_trace()
        #self.dialog.reload()
        for each_message_obj in self.dialog.utterances:
            output_str += "%d. %10s: %s\n" % (
            counter, each_message_obj.user, each_message_obj.text)
            counter += 1
        return output_str

    def print_dialog(self):
        serialized_dialog = self.serialize_dialog_dirty()
        print(serialized_dialog)

    def send_message_to_user(self, message_txt):
        """
        Interface to send messages to User (via Telegram or any other DialogBroker)

        This interface avoids DialogPlanner's functionality for merginf utterances.
        So use this method only if you know what you want to do!

        For discrete systems aware sending use `DialogPlanner.sendText` method.
        :return: self
        """
        self.dialog.reload()
        return self.dialog.send_message_to_user(message_txt)

    def show_latest_sys_responses(self):
        """
        Returns responses of the dialog system at current step (everything after the latest user message
        or the messages of the first step)
        :return: list of strings
        """
        sys_messages = self.filter_sys_messages_of_current_turn()
        sys_message_texts = [msg.text for msg in sys_messages]
        return sys_message_texts

    def filter_sys_messages_of_current_turn(self):
        """
        Return message objects of the dialog system at current step (everything after the latest
        user message or the messages of the first step)
        :return:
        """
        recent_user_messages = self.message_set.filter(author=self.user).order_by('-created_at')
        if recent_user_messages:
            recent_user_message_dt = recent_user_messages[0].created_at
            sys_messages = self.message_set.filter(author__user__username=DIALOG_SYSTEM_USER_NAME,
                                                   created_at__gte=recent_user_message_dt)
        else:
            sys_messages = self.message_set.filter(author__user__username=DIALOG_SYSTEM_USER_NAME)

        return sys_messages

    def list_user_messages(self):
        """
        Method used for prehistory analysis

        :return: list of user utterances since the start of the dialog.
        """
        self.dialog.reload()
        # user_indexes = self._user_messages_indexes()
        # user_answers = [self.dialog_acts[i] for i in user_indexes]
        target_human = self.dialog.get_target_user()
        user_messages = filter(lambda x: x.user == target_human, self.dialog.utterances)
        # user_messages = .filter(user=self.user)
        # user_messages = self.message_set.filter(author=self.user)
        user_answers = [msg.text for msg in user_messages]
        return user_answers

    def __getitem__(self, key):
        """
        retrieves message by numerical index of message
        :param key: int
        :return: Utterance
        """
        #message_obj = self.message_set.order_by("created_at")[key]

        utterance = self.dialog.utterances[key]
        return utterance

    @property
    def user(self):
        """
        interlocutor
        :return:
        """
        return self.target_user

    def __str__(self):
        return "Dialog with User: %s" % self.user