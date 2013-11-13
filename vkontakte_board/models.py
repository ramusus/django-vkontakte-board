# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from vkontakte_api.models import VkontakteManager, VkontakteModel, VkontakteContentError, VkontakteError
from vkontakte_api.decorators import fetch_all
from vkontakte_groups.models import Group
from vkontakte_users.models import User, ParseUsersMixin
from datetime import datetime
import logging

log = logging.getLogger('vkontakte_board')

class CommentManager(models.Manager):
    pass

class TopicManager(models.Manager):
    pass

class BoardRemoteManager(VkontakteManager, ParseUsersMixin):

    def parse_response(self, response, extra_fields=None):
        if isinstance(response, dict):
            self.parse_response_users(response)
            return super(BoardRemoteManager, self).parse_response_list(response[self.response_instances_fieldname], extra_fields)
        else:
            raise VkontakteContentError('Vkontakte response should be dict')

class TopicRemoteManager(BoardRemoteManager):

    response_instances_fieldname = 'topics'

    @fetch_all(default_count=100)
    def fetch(self, group, ids=None, extended=False, order=None, offset=0, count=100, preview=0, preview_length=90, **kwargs):
        #gid
        #ID группы, список тем которой необходимо получить.
        kwargs['gid'] = group.remote_id
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

        kwargs['extra_fields'] = {'group_id': group.id}
        return super(TopicRemoteManager, self).fetch(**kwargs)

class CommentRemoteManager(BoardRemoteManager):

    response_instances_fieldname = 'comments'

    @fetch_all(default_count=100)
    def fetch(self, topic, extended=False, offset=0, count=100, sort='asc', need_likes=True, after=None, **kwargs):
        if count > 100:
            raise ValueError("Attribute 'count' can not be more than 100")
        if sort not in ['asc','desc']:
            raise ValueError("Attribute 'sort' should be equal to 'asc' or 'desc'")
        if sort == 'asc' and after:
            raise ValueError("Attribute sort should be equal to 'desc' with defined `after` attribute")

        #gid
        #ID группы, к обсуждениям которой относится указанная тема.
        kwargs['gid'] = topic.group.remote_id
        #tid
        #ID темы в группе
        kwargs['tid'] = topic.remote_id.split('_')[1]
        #extended
        #Если указать в качестве этого параметра 1, то будет возвращена информация о пользователях, являющихся авторами сообщений. По умолчанию 0.
        kwargs['extended'] = int(extended)
        #offset
        #Смещение, необходимое для выборки определенного подмножества сообщений.
        kwargs['offset'] = int(offset)
        # sort
        # порядок сортировки комментариев:
        # asc - хронологический
        # desc - антихронологический
        kwargs['sort'] = sort
        #count
        #Количество сообщений, которое необходимо получить (но не более 100). По умолчанию 20.
        kwargs['count'] = int(count)
        # need_likes
        # 1 - будет возвращено дополнительное поле likes. По умолчанию поле likes не возвращается.
        kwargs['need_likes'] = int(need_likes)

        if after:
            kwargs['_after'] = after

        kwargs['extra_fields'] = {'topic_id': topic.id}
        try:
            return super(CommentRemoteManager, self).fetch(**kwargs)
        except VkontakteError, e:
            if e.code == 100 and 'invalid tid' in e.description:
                log.error("Impossible to fetch comments for unexisted topic ID=%s" % topic.remote_id)
                return self.model.objects.none()
            else:
                raise e

class BoardAbstractModel(VkontakteModel):
    class Meta:
        abstract = True

    methods_namespace = 'board'
    slug_prefix = 'topic'

    remote_id = models.CharField(u'ID', max_length='50', help_text=u'Уникальный идентификатор', unique=True)

class Topic(BoardAbstractModel):
    class Meta:
        verbose_name = u'Дискуссия групп Вконтакте'
        verbose_name_plural = u'Дискуссии групп Вконтакте'
        ordering = ['remote_id']

    remote_pk_field = 'tid'

    group = models.ForeignKey(Group, verbose_name=u'Группа', related_name='topics')

    title = models.CharField(u'Заголовок', max_length=500)
    created = models.DateTimeField(u'Дата создания', db_index=True)
    updated = models.DateTimeField(u'Дата последнего сообщения', null=True, db_index=True)

    created_by = models.ForeignKey(User, related_name='topics_created', verbose_name=u'Пользователь, создавший тему')
    updated_by = models.ForeignKey(User, related_name='topics_updated', verbose_name=u'Пользователь, оставивший последнее сообщение')

    is_closed = models.BooleanField(u'Закрыта?', help_text=u'Тема является закрытой (в ней нельзя оставлять сообщения)')
    is_fixed = models.BooleanField(u'Прикреплена?', help_text=u'Тема является прилепленной (находится в начале списка тем)')

    comments_count = models.PositiveIntegerField(u'Число сообщений в теме', default=0, db_index=True)

    first_comment = models.TextField(u'Текст первого сообщения')
    last_comment = models.TextField(u'Текст последнего сообщения')

    objects = TopicManager()
    remote = TopicRemoteManager(remote_pk=('remote_id',), methods={
        'get': 'getTopics',
    })

    @property
    def slug(self):
        return self.slug_prefix + str(self.remote_id)

    def __unicode__(self):
        return self.title

    def parse(self, response):
        self.created_by = User.objects.get_or_create(remote_id=response.pop('created_by'))[0]
        self.updated_by = User.objects.get_or_create(remote_id=response.pop('updated_by'))[0]
        if 'comments' in response:
            response['comments_count'] = response.pop('comments')

        super(Topic, self).parse(response)

        if '_' not in str(self.remote_id):
            self.remote_id = '-%s_%s' % (self.group.remote_id, self.remote_id)

    def fetch_comments(self, *args, **kwargs):
        return Comment.remote.fetch(topic=self, *args, **kwargs)

class Comment(BoardAbstractModel):
    class Meta:
        verbose_name = u'Коммментарий дискуссии групп Вконтакте'
        verbose_name_plural = u'Коммментарии дискуссий групп Вконтакте'
        ordering = ['remote_id']

    topic = models.ForeignKey(Topic, verbose_name=u'Тема', related_name='comments')
    author = models.ForeignKey(User, related_name='topics_comments', verbose_name=u'Aвтор сообщения')
    date = models.DateTimeField(help_text=u'Дата создания', db_index=True)
    text = models.TextField(u'Текст сообщения')
    #attachments - присутствует только если у сообщения есть прикрепления, содержит массив объектов (фотографии, ссылки и т.п.). Более подробная информация представлена на странице Описание поля attachments

    # TODO: implement with tests
#    likes = models.PositiveIntegerField(u'Кол-во лайков', default=0)

    objects = CommentManager()
    remote = CommentRemoteManager(remote_pk=('remote_id',), methods={
        'get': 'getComments',
    })

    @property
    def slug(self):
        return self.slug_prefix + str(self.topic.remote_id) + '?post=' + self.remote_id.split('_')[2]

    def parse(self, response):
        self.author = User.objects.get_or_create(remote_id=response.pop('from_id'))[0]
        # TODO: add parsing attachments and polls
        if 'attachments' in response:
            response.pop('attachments')
        if 'poll' in response:
            response.pop('poll')

        super(Comment, self).parse(response)

        if '_' not in str(self.remote_id):
            self.remote_id = '%s_%s' % (self.topic.remote_id, self.remote_id)