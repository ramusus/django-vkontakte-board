# -*- coding: utf-8 -*-
from django.test import TestCase
from models import Topic
import simplejson as json

class VkontakteBoardTest(TestCase):
    pass

#    def test_fetch_user_relatives(self):
#
#        users = User.remote.fetch(ids=[1,6])
#
#        self.assertEqual(users[0].relatives.count(), 0)
#
#        users = User.remote.fetch(ids=[1,6])
#
#        self.assertEqual(users[0].relatives.count(), 1) # fix it, design decision needed
#        self.assertEqual(users[0].relatives.all()[0], users[1])
#
#    def test_fetch_user_friends(self):
#
#        self.assertEqual(User.objects.count(), 0)
#        user = User.remote.fetch(ids=[6])[0]
#        self.assertEqual(User.objects.count(), 1)
#        user.fetch_friends()
#        self.assertTrue(User.objects.count() > 100)
#        self.assertEqual(user.friends_users.count(), User.objects.count()-1)
#
#    def test_fetch_user(self):
#
#        self.assertEqual(User.objects.count(), 0)
#        users = User.remote.fetch(ids=[1,2])
#        self.assertEqual(len(users), 2)
#        self.assertEqual(User.objects.count(), 2)
#
#        self.assertEqual(users[0].remote_id, 1)
#        self.assertEqual(users[0].first_name, u'Павел')
#        self.assertEqual(users[0].last_name, u'Дуров')
#        self.assertEqual(users[0].twitter, u'durov')
#        self.assertEqual(users[0].livejournal, u'durov')
#        self.assertTrue(len(users[0].activity) > 0)
#        self.assertEqual(users[0].relation, 1)
#        self.assertEqual(users[0].wall_comments, False)
#
#        # test counters
#        users[0].update_counters()
#        self.assertTrue(users[0].followers > 0)
#        self.assertTrue(users[0].notes > 0)
#        self.assertTrue(users[0].sum_counters > 0)
#        self.assertTrue(users[0].counters_updated is not None)
#
#        # fetch another time
#        users = User.remote.fetch(ids=[1,2])
#        self.assertEqual(User.objects.count(), 2)
#
#        # test for keeping old counters
#        self.assertTrue(users[0].sum_counters > 0)
#        self.assertTrue(users[0].followers > 0)
#        self.assertTrue(users[0].counters_updated is not None)
#
    def test_parse_user(self):

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
                "comments":5045},
            ]
            }}'''
        instance = Topic.remote.parse_response_list(json.loads(response)['response']['topics'])[0]
        instance.save()

        self.assertEqual(instance.remote_id, 51443905)
        self.assertEqual(instance.title, u'Вопросы по поводу создания приложений')
        self.assertEqual(instance.created, datetime(2011,2,22,12,0,0))
        self.assertEqual(instance.created_by, User.objects.get(remote_id=1))
        self.assertEqual(instance.updated, datetime(2011,2,22,12,0,0))
        self.assertEqual(instance.updated_by, User.objects.get(remote_id=1))
        self.assertEqual(instance.is_closed, False)
        self.assertEqual(instance.is_fixed, True)
        self.assertEqual(instance.comments, 5045)


#    def test_bad_activity(self):
#
#        bad_activity = u'\u7b7e\u8b49\u10e1\u502c\udd0c\u9387\ud157\uaf0c\ub348\ua8b7\uf0c7\uca16\ufd54\u3fb8\uabbd\u9b3c\u8329\u5630\uee9e\u5b81\u5976\u1c90\u7916\u56b9\u49fc\u4884\ua6b8\u3a6c\u6160\u1c6e\u1da1\udfe5\u254a\u25e3\ua933\u7e2f\u92c6\ubd1b\u9877\u2a56\uf3c6\uc03c\u5036\u336b\uef31\u3caf\u5c3c\ucba3\u0ad0\uca00\u9552\u7f4e\u2e4e\u5d24\u4b7c\ucf0e\u41ba\u20e2\u0d32\u1d81\ue82e\uc009\u2fad\udb67\ue8b2\ua3f2\ub71c\uc631\u9ad8\u3abd\u0364\u70d7\uc49c\u0d95\u02ec\u65c4\ucc5c\udee7\u45ca\ufe2a\u38a5\uca5f\uc398\ue37e\u117b\xd5\ua3e5\ue2bc\u8aab\u53df\ua98f\u580f\uc1c5\u66bc\u6d24\uacae\u3115\uc1d6\ufdfd\uadee\u71f6\u5c62\u9e9e\u685a\u9939\ud8e8\u191f\u96b5\u7a62\u7598\ud1e3\u4e39\u5328\u63c9\u808b\u5265\u9890\uaa48\u88dc\u6b67\u7b24\u8d70\ufdb1\ua387\u0747\u80a9\u9eb6\uea60\u8f56\u6ae2\u862c\u201c\u2eb8\u1fda\ufd58\u7d90\u0cd8\u2231\u0fc9\ucfd3'
#        User.objects.create(remote_id=1, activity=bad_activity, sex=0)
#        self.assertEqual(User.objects.count(), 1)
#        self.assertEqual(User.objects.all()[0].activity, '')
#
#        good_activity = u'Хорошая строка, good string'
#        User.objects.create(remote_id=2, activity=good_activity, sex=0)
#        self.assertEqual(User.objects.count(), 2)
#        self.assertEqual(User.objects.all()[1].activity, good_activity)
#
#    def test_multiple_slug_users(self):
#
#        User.objects.create(remote_id=173613533, screen_name='mikhailserzhantov', sex=0)
#        User.objects.create(remote_id=174221855, screen_name='mikhailserzhantov', sex=0)
#        User.objects.create(remote_id=182224356, screen_name='mikhailserzhantov', sex=0)
#
#        self.assertEqual(User.remote.get_by_slug('mikhailserzhantov').remote_id, 182224356)
#        self.assertEqual(User.objects.deactivated().count(), 2)