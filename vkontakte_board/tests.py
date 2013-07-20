# -*- coding: utf-8 -*-
from django.test import TestCase
from models import Topic, User, Comment
from factories import TopicFactory
from vkontakte_groups.factories import GroupFactory
import simplejson as json

GROUP_ID = 16297716
TOPIC_ID = '-16297716_26523718'

class VkontakteBoardTest(TestCase):

    def test_parse_topic(self):

        response = '''
            {"response":{
                "topics":[1,
                    {"tid":51443905,
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
        instance = Topic.remote.parse_response(json.loads(response)['response'], {'group_id': GroupFactory.create(remote_id=GROUP_ID).id})[0]
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
                "comments":[5045,{
                    "id":11374,
                    "from_id":189814,
                    "date":1298365200,
                    "text":"При возникновении любых вопросов, связанных с разработкой приложений, в первую очередь следует обратиться к FAQ в группе &quot;Приложения на основе ВКонтакте API&quot;:<br>http:\/\/vkontakte.ru\/pages.php?id=4143397<br><br>В той же группе есть тема &quot;Обмен опытом&quot; (http:\/\/vkontakte.ru\/topic-2226515_3507340), которая тоже крайне рекомендуется к ознакомлению.<br><br>Если вышеозначенные ссылки не помогли - можно задать вопрос здесь.<br><br>Задавать вопросы в духе &quot;я ничего не понял, объясните кто-нибудь в личке&quot; не следует, они будут удаляться.<br><br>Не следует также задавать вопросы, относящиеся не к разработке, а к работе конкретных приложений - обращайтесь в официальные группы этих приложений."}
                ]
            }}'''
        instance = Comment.remote.parse_response(json.loads(response)['response'], {'topic_id': TopicFactory.create(remote_id=TOPIC_ID).id})[0]
        instance.save()

        self.assertEqual(instance.remote_id, '%s_11374' % TOPIC_ID)
        self.assertEqual(instance.topic.remote_id, TOPIC_ID)
        self.assertEqual(instance.author, User.objects.get(remote_id=189814))
        self.assertIsNotNone(instance.date)
        self.assertTrue(len(instance.text) > 10)

    def test_fetching_topics(self):

        group = GroupFactory.create(remote_id=GROUP_ID)
        group.fetch_topics()

        self.assertTrue(group.topics.count() > 10)

    def test_fetching_comments(self):

        group = GroupFactory.create(remote_id=GROUP_ID)
        topic = TopicFactory.create(remote_id=TOPIC_ID, group=group)

        comments = topic.fetch_comments(count=20, sort='desc')
        self.assertTrue(len(comments) == topic.comments.count() == 20)

        # testing `after` parameter
        after = Comment.objects.order_by('date')[0].date

        Comment.objects.all().delete()
        self.assertEqual(Comment.objects.count(), 0)

        comments = topic.fetch_comments(after=after, sort='desc')
        self.assertTrue(len(comments) == Comment.objects.count() == topic.comments.count() == 20)

        # testing `all` parameter
        Comment.objects.all().delete()
        self.assertEqual(Comment.objects.count(), 0)

        comments = topic.fetch_comments(all=True)
        self.assertTrue(len(comments) == Comment.objects.count() == topic.comments.count())
        self.assertTrue(topic.comments.count() > 20)

    def test_fetching_comments_of_deleted_topic(self):

        group = GroupFactory.create(remote_id=17589818)
        topic = TopicFactory.create(remote_id='-17589818_26390905', group=group)

        comments = topic.fetch_comments()
        self.assertEqual(topic.comments.count(), 0)
        self.assertEqual(topic.comments.count(), len(comments))
