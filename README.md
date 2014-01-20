Django Vkontakte Board
======================

[![PyPI version](https://badge.fury.io/py/django-vkontakte-board.png)](http://badge.fury.io/py/django-vkontakte-board) [![Build Status](https://travis-ci.org/ramusus/django-vkontakte-board.png?branch=master)](https://travis-ci.org/ramusus/django-vkontakte-board) [![Coverage Status](https://coveralls.io/repos/ramusus/django-vkontakte-board/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-vkontakte-board)

Приложение позволяет взаимодействовать с дисскуссиями групп через Вконтакте API используя стандартные модели Django

Установка
---------

    pip install django-vkontakte-board

В `settings.py` необходимо добавить:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'vkontakte_api',
        'vkontakte_places,
        'vkontakte_groups',
        'vkontakte_users',
        'vkontakte_board',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                         # to keep in DB expired access tokens
    OAUTH_TOKENS_VKONTAKTE_CLIENT_ID = ''                               # application ID
    OAUTH_TOKENS_VKONTAKTE_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_VKONTAKTE_SCOPE = ['ads,wall,photos,friends,stats']    # application scopes
    OAUTH_TOKENS_VKONTAKTE_USERNAME = ''                                # user login
    OAUTH_TOKENS_VKONTAKTE_PASSWORD = ''                                # user password
    OAUTH_TOKENS_VKONTAKTE_PHONE_END = ''                               # last 4 digits of user mobile phone

Покрытие методов API
--------------------

* [board.getTopics](http://vk.com/dev/board.getTopics) – возвращает список тем в обсуждениях указанной группы;
* [board.getComments](http://vk.com/dev/board.getComments) – возвращает список сообщений в указанной теме;

Примеры использования
---------------------

### Получение дискуссий группы через метод группы

    >>> from vkontakte_groups.models import Group
    >>> group = Group.remote.fetch(ids=[16297716])[0]
    >>> group.fetch_topics()
    [<Topic: ЭСТАФЕТА ОЛИМПИЙСКОГО ОГНЯ ► задаем вопросы в этой теме>,
     <Topic: ПРОМО-АКЦИЯ "ВСТРЕЧАЙ НОВЫЙ ГОД С ПРИЗАМИ! СОБЕРИ ТЁПЛУЮ КОМПАНИЮ МИШЕК!" ► вопросы и обсуждение>,
     '...(remaining elements truncated)...']

Дискуссии группы доступны через менеджер

    >>> group.topics.count()
    12

### Получение дискуссий группы через менеджер

    >>> from vkontakte_board.models import Topic
    >>> Topic.remote.fetch(group=group, all=True)
    [<Topic: ЭСТАФЕТА ОЛИМПИЙСКОГО ОГНЯ ► задаем вопросы в этой теме>,
     <Topic: ПРОМО-АКЦИЯ "ВСТРЕЧАЙ НОВЫЙ ГОД С ПРИЗАМИ! СОБЕРИ ТЁПЛУЮ КОМПАНИЮ МИШЕК!" ► вопросы и обсуждение>,
     '...(remaining elements truncated)...']

### Получение комментариев дискуссии через метод дискуссии

    >>> from vkontakte_groups.models import Group
    >>> from vkontakte_board.models import Topic
    >>> group = Group.remote.fetch(ids=[16297716])[0]
    >>> topic = Topic.remote.fetch(group=group, ids=[26523718])[0]
    >>> topic.fetch_comments()
    [<Comment: Comment object>,
     <Comment: Comment object>,
     '...(remaining elements truncated)...']

Комментарии дискуссии доступны через менеджер

    >>> topic[0].comments.count()
    39

### Получение комментариев дискуссии через менеджер

    >>> from vkontakte_groups.models import Group
    >>> from vkontakte_board.models import Topic, Comment
    >>> group = Group.remote.fetch(ids=[16297716])[0]
    >>> topic = Topic.remote.fetch(group=group, ids=[26523718])[0]
    >>> Comment.remote.fetch(topic=topic)
    [<Comment: Comment object>,
     <Comment: Comment object>,
     '...(remaining elements truncated)...']