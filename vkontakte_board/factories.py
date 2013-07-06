from vkontakte_groups.factories import GroupFactory
from vkontakte_users.factories import UserFactory
from models import Topic, Comment
from datetime import datetime
import factory
import random

class TopicFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Topic

    group = factory.SubFactory(GroupFactory)
    remote_id = factory.LazyAttributeSequence(lambda o, n: '-%s_%s' % (o.group.remote_id, n))

    created = datetime.now()
    comments_count = 1

    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

class CommentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Comment

    remote_id = factory.LazyAttributeSequence(lambda o, n: '%s_%s' % (o.topic.remote_id, n))
    topic = factory.SubFactory(TopicFactory)
    date = datetime.now()
    author = factory.SubFactory(UserFactory)