from django.conf.urls import patterns, include, url

from turin import views

urlpatterns = patterns('',
    url(r'^today', views.today, name='index'),
    url(r'^(?P<storyid>\d{8})', views.getStory, name='detail'),
)