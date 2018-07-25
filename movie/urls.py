# -*- coding=utf-8 -*-
from django.conf.urls import url
from movie import views
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
# from django.views.generic import


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    url(r'^mov/(?P<m_to_type>\d+)-(?P<m_to_area>\d+)-(?P<f_to_time_id>\d+)/(?P<sort>\w*)/(?P<pid>\d*)', views.movie_list, name='mov_list'),
    url(r'^tv/(?P<m_to_area>\d+)/(?P<sort>\w*)/(?P<pid>\d*)', views.tv_list, name='tv_list'),

    url(r'^mov/(?P<nid>\d{7})/', views.movietv_detail, name='mov_detail'),
    url(r'^tv/(?P<nid>\d{7})/', views.movietv_detail, name='tv_detail'),

    url(r'^add_reply/', views.movietv_comment_reply),
    url(r'^del_comment_reply/', views.del_comment_reply),


    url(r'^login/', views.user_login),
    url(r'^register/', views.register),
    url(r'^send_msg/', views.send_msg),
    url(r'^user_exists/', views.user_exists),
    url(r'^check_code/', views.check_code),
    url(r'^member/(?P<uid>\d+)/(?P<account>\w*)', views.member, name='member'),
    url(r'^logout/', views.user_logout),
    url(r'^collect/', views.collect),

    url(r'^new_review/', views.new_review),
    url(r'^revi/(?P<nid>\d*)(?P<category>\w*)', views.revi, name='revi_detail'),


    url(r'^revi_edit/', views.edit_revi),
    url(r'^revi_del/', views.del_revi),

    url(r'^cart', views.n_v),
    url(r'^vari', views.n_v),
    url(r'^vide', views.n_v),
    url(r'^mess', views.n_v),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


