# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
from vkontakte_api.admin import VkontakteModelAdmin
from models import Topic

class TopicAdmin(VkontakteModelAdmin):
    pass
#    def image_preview(self, obj):
#        return u'<a href="%s"><img src="%s" height="30" /></a>' % (obj.photo_big, obj.photo)
#    image_preview.short_description = u'Аватар'
#    image_preview.allow_tags = True
#
#    list_display = ('image_preview','first_name','last_name','vk_link','rate','sex','bdate','timezone','city','country','has_mobile','home_phone','mobile_phone',)
#    list_display_links = ('first_name','last_name')
#    list_filter = ('sex','has_mobile','timezone',)
#    search_fields = ('first_name','last_name','screen_name')
#
#    def get_readonly_fields(self, request, obj=None):
#        fields = super(UserAdmin, self).get_readonly_fields(request, obj)
#        return fields + ['friends_users']

admin.site.register(Topic, TopicAdmin)