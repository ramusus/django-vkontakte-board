from vkontakte_groups.factories import GroupFactory
from vkontakte_users.factories import UserFactory
from models import Topic
from datetime import datetime
import factory
import random

class TopicFactory(factory.Factory):
    FACTORY_FOR = Topic

    group = factory.SubFactory(GroupFactory)
    remote_id = factory.Sequence(lambda n: n)
    created = datetime.now()
    comments_count = 1

    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)
