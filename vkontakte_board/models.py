# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.utils.translation import ugettext as _
from datetime import datetime
from vkontakte_api.utils import api_call, VkontakteError
from vkontakte_api import fields
from vkontakte_api.models import VkontakteManager, VkontakteIDModel
from vkontakte_groups.models import Group
from vkontakte_users.models import User
from dateutil import parser
from datetime import timedelta, datetime
import logging

log = logging.getLogger('vkontakte_board')

#VKONTAKTE_USERS_INFO_TIMEOUT_DAYS = getattr(settings, 'VKONTAKTE_USERS_INFO_TIMEOUT_DAYS', 0)
#
#USER_SEX_CHOICES = ((1, u'жен.'),(2, u'муж.'))
#USER_RELATION_CHOICES = (
#    (1, u'Не женат / замужем'),
#    (2, u'Есть друг / подруга'),
#    (3, u'Помолвлен / помолвлена'),
#    (4, u'Женат / замужем'),
#    (5, u'Всё сложно'),
#    (6, u'В активном поиске'),
#    (7, u'Влюблён / влюблена'),
#)
#
#USER_PHOTO_DEACTIVATED_URL = 'http://vk.com/images/deactivated_b.gif'
#USER_NO_PHOTO_URL = 'http://vkontakte.ru/images/camera_a.gif'
#
class TopicManager(models.Manager):
    pass

class TopicRemoteManager(VkontakteManager):

    def fetch(self, ids=None, extended=False, order=None, offset=0, count=40, preview=0, preview_length=90, **kwargs):
        #tids
        #Список идентификаторов тем, которые необходимо получить (не более 100). По умолчанию возвращаются все темы. Если указан данный параметр, игнорируются параметры order, offset и count (возвращаются все запрошенные темы в указанном порядке).
        if ids and isinstance(ids, (list, tuple)):
            kwargs['tids'] = ','.join(map(lambda i: str(i), ids))
        #extended
        #Если указать в качестве этого параметра 1, то будет возвращена информация о пользователях, являющихся создателями тем или оставившими в них последнее сообщение. По умолчанию 0.
        kwargs['extended'] = int(extended)
        #order
        #Порядок, в котором необходимо вернуть список тем. Возможные значения:
        #1 - по убыванию даты обновления,
        #2 - по убыванию даты создания,
        #-1 - по возрастанию даты обновления,
        #-2 - по возрастанию даты создания.
        #По умолчанию темы возвращаются в порядке, установленном администратором группы. "Прилепленные" темы при любой сортировке возвращаются первыми в списке.
        if order:
            kwargs['order'] = int(order)
        #offset
        #Смещение, необходимое для выборки определенного подмножества тем.
        kwargs['offset'] = int(offset)
        #count
        #Количество тем, которое необходимо получить (но не более 100). По умолчанию 40.
        kwargs['count'] = int(count)
        #preview
        #Набор флагов, определяющий, необходимо ли вернуть вместе с информацией о темах текст первых и последних сообщений в них. Является суммой флагов:
        #1 - вернуть первое сообщение в каждой теме (поле first_comment),
        #2 - вернуть последнее сообщение в каждой теме (поле last_comment). По умолчанию 0 (не возвращать текст сообщений).
        kwargs['preview'] = int(preview)
        #preview_length
        #Количество символов, по которому нужно обрезать первое и последнее сообщение. Укажите 0, если Вы не хотите обрезать сообщение. (по умолчанию 90).
        kwargs['preview_length'] = int(preview_length)

        super(TopicRemoteManager, self).fetch(**kwargs)

    def get(self, *args, **kwargs):
        '''
        Retrieve objects from remote server
        '''
        response_list = self.api_call(*args, **kwargs)

        users = User.remote.parse_response_list(response_list['users'])
        print users
        return self.parse_response_list(response_list['topics'])

class Topic(VkontakteIDModel):
    '''
    '''
    class Meta:
        db_table = 'vkontakte_board_topic'
        verbose_name = _('Vkontakte group topic')
        verbose_name_plural = _('Vkontakte group topics')
        ordering = ['remote_id']

    remote_pk_field = 'tid'
    methods_namespace = 'boards'
    slug_prefix = 'board'

    group = models.ForeignKey(Group, verbose_name=u'Группа')

    title = models.CharField(u'Заголовок', max_length=500)
    created = models.DateTimeField(help_text=u'Дата создания')
    updated = models.DateTimeField(null=True, help_text=u'дата последнего сообщения')

    created_by = models.ForeignKey(User, verbose_name=u'Пользователь, создавшего тему')
    updated_by = models.ForeignKey(User, verbose_name=u'Пользователь, оставившего последнее сообщение')

    is_closed = models.BooleanField(u'Закрыта?', help_text=u'Тема является закрытой (в ней нельзя оставлять сообщения)')
    is_fixed = models.BooleanField(u'Прикреплена?', help_text=u'Тема является прилепленной (находится в начале списка тем)')

    comments = models.PositiveIntegerField(u'Число сообщений в теме')

    first_comment = models.TextField(u'Текст первого сообщения')
    last_comment = models.TextField(u'Текст последнего сообщения')

    objects = TopicManager()
    remote = TopicRemoteManager(remote_pk=('remote_id',), methods={
        'get': 'getTopics',
    })


    def __unicode__(self):
        return self.title

    def fetch_comments(self, *args, **kwargs):
        pass
#        if 'vkontakte_wall' in settings.INSTALLED_APPS:
#            from vkontakte_wall.models import Post
#            return Post.remote.fetch_user_wall(self, *args, **kwargs)
#        else:
#            raise ImproperlyConfigured("Application 'vkontakte_wall' not in INSTALLED_APPS")