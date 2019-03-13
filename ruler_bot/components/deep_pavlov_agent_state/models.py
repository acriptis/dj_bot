from mongoengine import Document, DynamicDocument, ReferenceField, ListField, StringField, DynamicField, \
    UUIDField, DateTimeField, FloatField, DictField


class User(Document):
    user_type = StringField(required=True, choices=['human', 'bot'], default='human')
    personality = DynamicField()

    meta = {'allow_inheritance': True}

    def to_dict(self):
        return {'id': str(self.id),
                'user_type': self.user_type,
                'personality': self.personality}

    @classmethod
    def get_or_create(cls, *args, **kwargs):
        """
        Gets or creates an object from init specification

        Args:
            *args:
            **kwargs:

        Returns:
            tuple: (instance:cls, is_created:bool)
                instance - is an object of the Class provided for arguments.
                is_created - True if the instance created from provided arguments, False otherwise

        Raises:
            Exception: For multiple instances of the provided filter.

        """
        results = cls.objects(*args, **kwargs)
        if results:
            if len(results) > 1:
                raise Exception(
                    f"Multiple instances found for {cls.__name__}: ({args}, {kwargs})!")
            elif len(results) == 1:
                return results[0], False
        else:
            instance = cls(*args, **kwargs)
            instance.save()
            return instance, True


class Human(User):
    username = StringField(required=True, unique=True)
    # user_telegram_id = StringField(required=True, unique=True)
    device_type = DynamicField()

    def to_dict(self):
        return {'id': str(self.id),
                'username': str(self.username),
                # 'user_telegram_id': str(self.user_telegram_id),
                'user_type': self.user_type,
                'device_type': self.device_type,
                'personality': self.personality}


class Utterance(Document):
    text = StringField(required=True)
    annotations = DictField(default={'ner': {}, 'coref': {}, 'sentiment': {}})
    user = ReferenceField(User, required=True)
    date_time = DateTimeField(required=True)

    meta = {'allow_inheritance': True}

    def to_dict(self):
        return {'id': str(self.id),
                'text': self.text,
                'user_id': str(self.user.id),
                'annotations': self.annotations,
                'date_time': str(self.date_time)}

    @classmethod
    def create_message(cls, text, author):
        """
        Template for creation of simple messages from text and author
        Args:
            text: str
            author: User

        Returns:

        """
        import datetime as dt
        return cls(text=text, user=author, date_time=dt.datetime.utcnow()).save()

class BotUtterance(Utterance):
    active_skill = StringField()
    confidence = FloatField()

    def to_dict(self):
        return {
            'id': str(self.id),
            'active_skill': self.active_skill,
            'confidence': self.confidence,
            'text': self.text,
            'user_id': str(self.user.id),
            'annotations': self.annotations,
            'date_time': str(self.date_time)
        }


class Dialog(DynamicDocument):
    location = DynamicField()
    utterances = ListField(ReferenceField(Utterance), required=False, default=[])
    users = ListField(ReferenceField(User), required=True)
    channel_type = StringField(choices=['telegram', 'vkontakte', 'facebook'], default='telegram')

    def to_dict(self):
        return {
            'id': str(self.id),
            'location': self.location,
            'utterances': [utt.to_dict() for utt in self.utterances],
            'user': [u.to_dict() for u in self.users if u.user_type == 'human'][0],
            'bot': [u.to_dict() for u in self.users if u.user_type == 'bot'][0],
            'channel_type': self.channel_type
        }

    def _push_dialog_act(self, author, message):
        """
        Method used for putting new message into data model of dialog
        Args:
            author: User which is author of the message
            message: str: text of the message

        Returns: Utterance

        """
        # print("Pushing Dialog ACT")
        utt=Utterance.create_message(text=message, author=author)
        self.utterances.append(utt)
        self.save()
        return utt

    def send_message_to_user(self, message_txt):
        """
        Interface to send messages to User (via Telegram or any other DialogBroker)
        :return: self
        """
        if not message_txt:
            import ipdb;
            ipdb.set_trace()
            print("empty message?")

        sys_user, is_created = User.get_or_create(user_type='bot')
        return self._push_dialog_act(sys_user, message_txt)

    def get_target_user(self):
        """
        Finds a HumanUser account in list of participants of dialog

        Returns: Human

        """
        humans = list(filter(lambda x: isinstance(x, Human), self.users))
        assert len(humans) == 1
        return humans[0]

    #def __getitem__(self, item):
    #    """
    #    Returns utterance in dialog by number of step
    #    """
    #    return self.utterances[item]