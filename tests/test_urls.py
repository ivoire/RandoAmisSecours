from django.conf.urls import include, url
from django.contrib import admin

from RandoAmisSecours import urls as ras_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(ras_urls)),
]
