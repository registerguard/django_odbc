from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_odbc.views.home', name='home'),
    # url(r'^django_odbc/', include('django_odbc.foo.urls')),
    url(r'categories/', 'turin.views.categories', name='categories'),
    (r'news/', include('turin.urls')),
    url(r'^$', 'turin.views.show_url_patterns', name='urls'),

    # Uncomment the admin/doc line below to enable admin documentation:
#     url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#     url(r'^admin/', include(admin.site.urls)),
)
