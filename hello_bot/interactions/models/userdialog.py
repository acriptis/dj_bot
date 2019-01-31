from django.db import models
from bank_bot.settings import DIALOG_SYSTEM_USER_NAME, DEFAULT_USER_NAME
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class DPUserProfile(models.Model):
    """
    DeepPavlov User Profile
    for keeping domain specific attributes of UserModels

    A simple model for users which can be participants of Dialogs

    creates user on fly by name

    OneToOne field
    https://habr.com/post/313764/#OneToOneField

    #TODO generally it must be
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            DPUserProfile.objects.create(user=instance)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()

    @classmethod
    def get_or_create_userprofile(cls, username, email=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not password:
            # TODO remove hardcode?
            password = "password"
        if not email:
            email = "dummy@mail.com"
        try:
            user = User.objects.get(username=username, email=email)
        except Exception as e:

            user = User.objects.create_user(username=username, password=password, email=email)

        dp_userprofile, _ = DPUserProfile.objects.get_or_create(user=user)

        return dp_userprofile

    def __str__(self):
        return "@%s" % self.user.username


class Message(models.Model):
    """
    A message in some UserDialog

    """
    userdialog = models.ForeignKey("UserDialog", on_delete=models.CASCADE)
    author = models.ForeignKey(DPUserProfile, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s: %s" % (self.author, self.text)


class UserDialog(models.Model):
    """
    Dialog between System and User (2 participants)
    """
    # user, with which we talk (interlocutor):
    target_user = models.ForeignKey(DPUserProfile, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_message = ""

        # self.active_user_interactions = []

        # # list of QuestionInteractions waiting for response
        # self.questions_under_discussion = []

    def _push_dialog_act(self, author, message):
        """
        :param author:
        :param message:
        :return:
        """
        message = Message.objects.create(userdialog=self, author=author, text=message)
        self.last_message = message

        return self

    def serialize_dialog_dirty(self):
        """
        Console Friendly and Human Readable dialog representation

        :return: output_str - formatted string with names, turn numbers and message texts
        """
        messages = Message.objects.filter(userdialog=self).order_by('created_at')

        output_str = ""
        # zipped_messages = list(zip(self.dialog_speakers, self.dialog_acts))
        counter = 0
        for each_message_obj in messages:
            output_str += "%d. %10s: %s\n" % (
            counter, each_message_obj.author, each_message_obj.text)
            counter += 1
        return output_str

    def print_dialog(self):
        serialized_dialog = self.serialize_dialog_dirty()
        print(serialized_dialog)

    def send_message_to_user(self, message_txt):
        """
        Interface to send messages to User (via Telegram or any other DialogBroker)
        :return: self
        """
        if not message_txt:
            import ipdb;
            ipdb.set_trace()
            print("empty message?")
        sys_user = DPUserProfile.get_or_create_userprofile(DIALOG_SYSTEM_USER_NAME)
        return self._push_dialog_act(sys_user, message_txt)

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
        # user_indexes = self._user_messages_indexes()
        # user_answers = [self.dialog_acts[i] for i in user_indexes]
        user_messages = self.message_set.filter(author=self.user)
        user_answers = [msg.text for msg in user_messages]
        return user_answers

    def __getitem__(self, key):
        """
        retrieves message by numerical index of message
        :param key: int
        :return: message
        """
        message_obj = self.message_set.order_by("created_at")[key]
        return message_obj.text

    @property
    def user(self):
        """
        interlocutor
        :return:
        """
        return self.target_user

    def __str__(self):
        return "Dialog with User: %s" % self.user
