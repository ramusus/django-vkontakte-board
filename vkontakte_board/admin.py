# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
from vkontakte_api.admin import VkontakteModelAdmin
from models import Topic, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    can_delete = False
    fields = ('author','text','date')
    readonly_fields = fields

class TopicAdmin(VkontakteModelAdmin):
    list_display = ('group','title','created','updated')
    list_display_links = ('title',)
#    list_filter = ('group',)
    search_fields = ('text',)
#    exclude = ('like_users','repost_users',)
    inlines = [CommentInline]

admin.site.register(Topic, TopicAdmin)