from django.conf.urls import url
from users.views import *


urlpatterns = [
    url(
        r'^update/$',
        UserUpdateView.as_view(),
        name="user-update"
    ),
    url(
        r'^(?P<username>.*)/friends/$',
        FriendFollowingView.as_view(),
        name="friend-following"
    ),
    url(
        r'^follow/$',
        FollowView.as_view(),
        name='follow'
    ),
    url(
        r'^(?P<username>.*)/cryptsy/(?P<credential_id>\d+)/checkpoint/$',
        UserCryptsyNotificationToken.as_view(),
        name='cryptsy_notification_token'
    ),
    url(
        r'^i/(?P<object_name>.*)/(?P<object_id>\d+)/$',
        ConversationInviteView.as_view(),
        name="user-conversation-invite"
    ),
    url(
        r'^i/(?P<token>.*)/$',
        ConversationInviteView.as_view(),
        name="user-conversation-invite"
    ),
    url(
        r'^(?P<slug>.*)/$',
        UserDetailView.as_view(),
        name="user-detail"
    ),
]
