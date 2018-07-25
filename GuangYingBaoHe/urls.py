from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('movie.urls')),
    url(r'^search/', include('haystack.urls')),
]