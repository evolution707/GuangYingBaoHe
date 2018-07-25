# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import MovieAndTv, MovieAndTvType, MovieAndTvArea, MovieAndTvTime, UserInfo, Review
from guardian.admin import GuardedModelAdmin


# 调整页面头部显示内容和页面标题
# class MyAdminSite(admin.AdminSite):
#     site_header = '光影宝盒后台管理'
#     site_title = '光影宝盒'
#     fields = ('id','title','director','writer','actor','grade','language','other_name','intro','ctime')
#
# admin_site = MyAdminSite(name='management')
#
# admin_site.register([MovieAndTv,MovieAndTvType,MovieAndTvArea])


# 配置需要的显示的相关字段
class MyAdminSite(admin.ModelAdmin):
    list_display = ('id', 'title', 'director', 'writer', 'actor', 'type', 'grade', 'language',
                    'other_name', 'intro', 'cd', 'min', 'release_date', 'debut', 'ctime')
    search_fields = ('title', 'id','director', 'actor', 'type', 'num')


# class UserAdmin(GuardedModelAdmin):
#     pass
# admin.site.register(UserInfo, UserAdmin)


admin.site.register(MovieAndTv, MyAdminSite)
admin.site.register(UserInfo)
admin.site.register([MovieAndTvType, MovieAndTvArea, MovieAndTvTime])
admin.site.register(Review)
