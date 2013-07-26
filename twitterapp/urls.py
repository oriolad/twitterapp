from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'tweet.views.index'),
    url(r'^logout/$','tweet.views.logout'),
    url(r'^twitter/$','tweet.views.twitter'),
    url(r'^usersearch/$','tweet.views.usersearch'),
    url(r'^userfound/$','tweet.views.userfound'),
    url(r'^usermanagement/$', 'tweet.views.usermanagement')
)
