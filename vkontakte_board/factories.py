from models import Topic
import factory
import random

class TopicFactory(factory.Factory):
    FACTORY_FOR = Topic

    remote_id = factory.Sequence(lambda n: n)