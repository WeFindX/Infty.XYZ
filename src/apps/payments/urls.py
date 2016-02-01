from django.conf.urls import url

from .views import *


urlpatterns = [
    url(
        r'^paypal/(?P<comment_id>\d+)/$',
        PayPalTransactionView.as_view(),
        name='transaction_paypal'
    ),
    url(
        r'^paypal/success/$',
        PayPalTransactionSuccessView.as_view(),
        name='transaction_paypal_success'
    ),
    url(
        r'^cryptsy/(?P<comment_id>\d+)/$',
        CryptsyTransactionCreateView.as_view(),
        name='transaction_cryptsy'
    ),
    url(
        r'^cryptsy/credential/create/$',
        CryptsyCredentialCreateView.as_view(),
        name='cryptsy_credential_create'
    ),
    url(
        r'^cryptsy/credential/update/(?P<pk>\d+)/$',
        CryptsyCredentialUpdateView.as_view(),
        name='cryptsy_credential_update'
    ),
    url(
        r'^cryptsy/credential/list/$',
        CryptsyCredentialListView.as_view(),
        name='cryptsy_credential_list'
    ),
    url(
        r'^cryptsy/credential/delete/(?P<pk>\d+)/$',
        CryptsyCredentialDeleteView.as_view(),
        name='cryptsy_credential_delete'
    ),
    url(
        r'^coin/address/list/$',
        CoinAddressListView.as_view(),
        name='coin_address_list'
    ),
    url(
        r'^coin/address/create/$',
        CoinAddressCreateView.as_view(),
        name='coin_address_create'
    ),
    url(
        r'coin/address/update/(?P<slug>\d+)/$',
        CoinAddressUpdateView.as_view(),
        name='coin_address_update'
    ),
    url(
        r'coin/address/delete/(?P<slug>\d+)/$',
        CoinAddressDeleteView.as_view(),
        name='coin_address_delete'
    ),
]
