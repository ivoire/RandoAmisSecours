from django.conf.urls import patterns, include, url

from RandoAmisSecours import urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('RandoAmisSecours.urls')),
)
