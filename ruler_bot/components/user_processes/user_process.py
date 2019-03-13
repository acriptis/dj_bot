from mongoengine import DynamicDocument, StringField, ReferenceField, Document

from components.user_domains.models import UserDomain
from mongoengine.queryset.base import CASCADE
from components.utils.mongoengine_get_or_create_mixin import MongoEngineGetOrCreateMixin


class UserProcess(Document, MongoEngineGetOrCreateMixin):
    """
    Generic class of stateful process used for Interactions and Slots Processing
    """
    meta = {"abstract": True}

    INIT = 'Init'
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'
    IGNORED = 'Ignored'
    INTERACTION_STATES = (
        (INIT, 'init'),
        (ACTIVE, 'Active'),
        (IGNORED, 'Ignored'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    )

    user_domain = ReferenceField(UserDomain, reverse_delete_rule=CASCADE)

    state = StringField(required=True, choices=INTERACTION_STATES, default=INIT)
