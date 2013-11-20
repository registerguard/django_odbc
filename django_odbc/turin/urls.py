from django.conf.urls import patterns, include, url

from turin import views

urlpatterns = patterns('',
    url(r'^today/$', views.today, name='index'),
    url(r'^welch/$', views.welchIndex, name='welch'),
    url(r'^(?P<storyid>\d{8})/no-layout/$', views.getStory, {'onLayout': False}, name='detail_no_layout'),
    url(r'^(?P<storyid>\d{8})/$', views.getStory, {'onLayout': True}, name='detail'),
    url(r'^status/$', views.status, name='status'),
    url(r'^updates/$', views.updates, name='updates'),
    url(r'^thumbnail/(?P<imageid>\d+)/$', views.thumbnail, name='image'),
)
