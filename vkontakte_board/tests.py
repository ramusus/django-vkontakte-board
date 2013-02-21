# -*- coding: utf-8 -*-
from django.test import TestCase
from models import Topic, User, Comment
from factories import TopicFactory
from vkontakte_groups.factories import GroupFactory
import simplejson as json
from datetime import datetime

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
                "updated":1298365200,
                "updated_by":1,
                "is_closed":0,
                "is_fixed":1,
                "comments":5045}
            ]
            }}'''
        instance = Topic.remote.parse_response_list(json.loads(response)['response'], {'group_id': GroupFactory.create(remote_id=GROUP_ID).id})[0]
        instance.save()

        self.assertEqual(instance.remote_id, '-%s_51443905' % GROUP_ID)
        self.assertEqual(instance.title, u'Вопросы по поводу создания приложений')
        self.assertEqual(instance.created, datetime(2011,2,22,9,0,0))
        self.assertEqual(instance.created_by, User.objects.get(remote_id=1))
        self.assertEqual(instance.updated, datetime(2011,2,22,9,0,0))
        self.assertEqual(instance.updated_by, User.objects.get(remote_id=1))
        self.assertEqual(instance.is_closed, False)
        self.assertEqual(instance.is_fixed, True)
        self.assertEqual(instance.comments_count, 5045)

    def test_parse_comment(self):

        response = '''
            {"response":{"comments":[5045,{
                "id":11374,
                "from_id":189814,
                "date":1298365200,
                "text":"При возникновении любых вопросов, связанных с разработкой приложений, в первую очередь следует обратиться к FAQ в группе &quot;Приложения на основе ВКонтакте API&quot;:<br>http:\/\/vkontakte.ru\/pages.php?id=4143397<br><br>В той же группе есть тема &quot;Обмен опытом&quot; (http:\/\/vkontakte.ru\/topic-2226515_3507340), которая тоже крайне рекомендуется к ознакомлению.<br><br>Если вышеозначенные ссылки не помогли - можно задать вопрос здесь.<br><br>Задавать вопросы в духе &quot;я ничего не понял, объясните кто-нибудь в личке&quot; не следует, они будут удаляться.<br><br>Не следует также задавать вопросы, относящиеся не к разработке, а к работе конкретных приложений - обращайтесь в официальные группы этих приложений."
                },{"id":11378,"from_id":51550980,"date":1260721960,"text":"Возможно ли будет в будущем в контейнере вызвать showInviteBox с массивом уже отмеченных для приглашения друзей?"},{"id":11382,"from_id":1775328,"date":1260722859,"text":"Не совсем понял где писать, но решил написать здесь ... буквально неделю назад моё приложение заблокировали, а в причине написали нарушение правил пункт 5 в подписи. исправил, это не сложно, все возобновили.. НО.. ведь подобные нарушения замечены почти у всех приложений......<br>даже у таких популярных как это<br>http:\/\/vkontakte.ru\/app630896<br><br>вопрос. неужели правила не для всех едины?"},{"id":11394,"from_id":3908342,"date":1260729642,"text":"Егор Bicoz Филиппов, иногда администрация делает исключения на ссылки, которые ведут на официальные форумы.<br><br>Насколько помню, то сообщение от администрации было примерно такого плана: &quot;мы можем сделать исключения только в тех случаях, когда возможностей групп вконтакте недостаточно для поддержки приложения&quot;. Что-то типа того.<br><br>З.Ы. Егор и другие пользователи, которые будут выкладывать ссылки на приложения, убирайте пожалуйста реф-часть."}]}}'''
        instance = Comment.remote.parse_response_list(json.loads(response)['response'])[0]
        instance.topic = TopicFactory.create()
        instance.save()

        self.assertEqual(instance.remote_id, 11374)
        self.assertEqual(instance.author, User.objects.get(remote_id=189814))
        self.assertEqual(instance.date, datetime(2011,2,22,9,0,0))
        self.assertTrue(len(instance.text) > 10)

    def test_fetching_topics(self):

        group = GroupFactory.create(remote_id=GROUP_ID)
        group.fetch_topics()

        self.assertTrue(group.topics.count() > 10)

    def test_fetching_comments(self):

        group = GroupFactory.create(remote_id=GROUP_ID)
        topic = TopicFactory.create(remote_id=TOPIC_ID, group=group)

        topic.fetch_comments()
        self.assertEqual(topic.comments.count(), 20)

        topic.fetch_comments(all=True)
        self.assertTrue(topic.comments.count() > 20)