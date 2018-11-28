from django.db import models
# from hello_bot.hello_bot.settings import SYSTEM_USER_NAME
from bank_bot.settings import SYSTEM_USER_NAME


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
        """
        Returns responses of the dialog system at current step (everything after the latest user message
        or the messages of the first step)
        :return:
        """
        # import ipdb; ipdb.set_trace()
        # find highest non sys index:
        user_indexes = [i for i, x in enumerate(self.dialog_speakers) if x != SYSTEM_USER_NAME]
        # import ipdb; ipdb.set_trace()

        max_user_index = max(user_indexes)

        # find system responses after latest user input:
        latest_sys_indexes = [i for i, x in enumerate(self.dialog_speakers) if (x == SYSTEM_USER_NAME and i>max_user_index)]
        sys_answers = [self.dialog_acts[i] for i in latest_sys_indexes]
        return sys_answers
