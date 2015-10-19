from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf.urls.static import static
import settings
from django.views.generic.base import TemplateView

admin.autodiscover()

handler500 = "django.views.defaults.server_error"

urlpatterns = patterns('',

    # Web home
    url(r"^$",          TemplateView.as_view(template_name='index.html')),
    url(r'^admin/',     include(admin.site.urls)),
    
    url(r'^vision',     include('vision.urls')),
    
)

if settings.DEBUG:
    # Used in debug mode for handling user-uploaded files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += patterns("", url(r'^v1/tests', include('runtests.urls')))

