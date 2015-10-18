from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from core.views import IndexView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^w$', IndexView.as_view(), name='wider'),
    url(r'', include('apps.core.urls')),
    url(r'^user/', include('allauth.urls')),
    url(r'^user/', include('apps.users.urls')),
    url(r'^payments/', include('payments.urls', namespace="payments")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ext/', include('django_select2.urls')),
    url(r'^invite/', include('invitation.urls', namespace='invite')),
    url(r'^help/$', TemplateView.as_view(template_name='help.html'),
        name="help"),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name="about"),
    url(r'^story/$', TemplateView.as_view(template_name='story.html'),
        name="story"),
    url(r'^policy/$', TemplateView.as_view(template_name='policy.html'),
        name="policy"),
    url('^markdown/', include( 'django_markdown.urls')),
    url('^i18n/', include('django.conf.urls.i18n')),
)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
