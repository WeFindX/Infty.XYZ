from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

from core.views import IndexView, DefinitionCreateView, SetLanguageView

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^set-lang/(?P<lang>\w+)/$', SetLanguageView.as_view(pattern_name='home'), name='lang_redirect'),
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^[!]$', IndexView.as_view(), name='index'),
    url(r'^i$', IndexView.as_view(), name='inbox'),
    url(r'', include('apps.core.urls')),
    url(r'^user/', include('allauth.urls')),
    url(r'^user/', include('apps.users.urls')),
    url(r'^payments/', include('payments.urls', namespace="payments")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^invite/', include('invitation.urls', namespace='invite')),
    url(r'^help/$', TemplateView.as_view(template_name='help.html'),
        name="help"),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name="about"),
    url(r'^story/$', TemplateView.as_view(template_name='story.html'),
        name="story"),
    url(r'^policy/$', TemplateView.as_view(template_name='policy.html'),
        name="policy"),
    url(r'^membership/$', TemplateView.as_view(template_name='membership.html'),
        name="membership"),
    url(r'^dev/$', TemplateView.as_view(template_name='dev.html'),
        name="dev"),
    url(r'^data/$', TemplateView.as_view(template_name='data.html'),
        name="data"),
    url('^markdown/', include('django_markdown.urls')),
    url('^i18n/', include('django.conf.urls.i18n')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)),]
