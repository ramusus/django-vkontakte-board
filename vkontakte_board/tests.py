# -*- coding: utf-8 -*-
from vkontakte_groups.factories import GroupFactory
from vkontakte_api.tests import VkontakteApiTestCase
import simplejson as json

from .models import Topic, User, Comment
from .factories import TopicFactory


GROUP_ID = 16297716
TOPIC_ID = '-16297716_26523718'


class VkontakteBoardTest(VkontakteApiTestCase):

    def test_parse_topic(self):

        response = '''
            {"response":{
                "count":1,
                "items":[
                    {"id":51443905,
                    "title":"Вопросы по поводу создания приложений",
                    "created":1298365200,
                    "created_by":1,
                    "updated":0,
                    "updated_by":1,
                    "is_closed":0,
                    "is_fixed":1,
                    "comments":5045}
                ]
            }}'''
        instance = Topic.remote.parse_response(json.loads(response)['response'], {
            'group_id': GroupFactory(remote_id=GROUP_ID).pk})[0]
        instance.save()

        self.assertEqual(instance.remote_id, '-%s_51443905' % GROUP_ID)
        self.assertEqual(instance.group.remote_id, GROUP_ID)
        self.assertEqual(instance.title, u'Вопросы по поводу создания приложений')
        self.assertEqual(instance.created_by, User.objects.get(remote_id=1))
        self.assertEqual(instance.updated_by, User.objects.get(remote_id=1))
        self.assertEqual(instance.is_closed, False)
        self.assertEqual(instance.is_fixed, True)
        self.assertEqual(instance.comments_count, 5045)
        self.assertIsNotNone(instance.created)
        self.assertIsNone(instance.updated)

    def test_parse_comment(self):

        response = '''
            {"response":{
                "count":1,
                "items":[
                    {"id":11374,
                    "from_id":189814,
                    "date":1298365200,
                    "text":"При возникновении любых вопросов, связанных с разработкой приложений, в первую очередь"}
                ]
            }}'''
        instance = Comment.remote.parse_response(json.loads(response)['response'], {
            'topic_id': TopicFactory(remote_id=TOPIC_ID).pk})[0]
        instance.save()

        self.assertEqual(instance.remote_id, '%s_11374' % TOPIC_ID)
        self.assertEqual(instance.topic.remote_id, TOPIC_ID)
        self.assertEqual(instance.author, User.objects.get(remote_id=189814))
        self.assertIsNotNone(instance.date)
        self.assertTrue(len(instance.text) > 10)

    def test_fetch_topics(self):

        group = GroupFactory(remote_id=GROUP_ID)
        group.fetch_topics()

        self.assertTrue(group.topics.count() > 10)

        topics = group.fetch_topics(all=True, extended=True)

        self.assertTrue(topics.count() > 10)

    def test_fetch_comments(self):

        group = GroupFactory(remote_id=GROUP_ID)
        topic = TopicFactory(remote_id=TOPIC_ID, group=group)

        comments = topic.fetch_comments(count=20, sort='desc')
        self.assertEqual(len(comments), topic.comments.count())
        self.assertEqual(len(comments), 20)

        # testing `after` parameter
        after = Comment.objects.order_by('date')[0].date

        Comment.objects.all().delete()
        self.assertEqual(Comment.objects.count(), 0)

        comments = topic.fetch_comments(after=after, sort='desc')
        self.assertEqual(len(comments), Comment.objects.count())
        self.assertEqual(len(comments), topic.comments.count())
        self.assertEqual(len(comments), 20)

        # testing `all` parameter
        Comment.objects.all().delete()
        self.assertEqual(Comment.objects.count(), 0)

        comments = topic.fetch_comments(all=True)
        self.assertEqual(len(comments), Comment.objects.count())
        self.assertEqual(len(comments), topic.comments.count())
        self.assertTrue(len(comments) > 20)

    def test_fetch_comments_of_deleted_topic(self):

        group = GroupFactory(remote_id=17589818)
        topic = TopicFactory(remote_id='-17589818_26390905', group=group)

        comments = topic.fetch_comments()
        self.assertEqual(topic.comments.count(), 0)
        self.assertEqual(topic.comments.count(), len(comments))
