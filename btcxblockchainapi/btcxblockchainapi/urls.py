#from django.conf.urls import patterns, include, url
from django.conf.urls import include, url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
#from quickstart import views
#from btcrpc import views
from btcrpc.view.check_wallets_balance import CheckWalletsBalance
from btcrpc.view.send_many_view import BTCSendManyView
from btcrpc.view.transfer_using_sendtoaddress import TransferCurrencyByUsingSendTaoAddress
from btcrpc.views import *
from quickstart.views import *
from btcrpc.view.balance import *
from btcrpc.view.send import *
from btcrpc.view.addresses import *
from btcrpc.view.check_multi_receives import *


from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users',  UserViewSet)
router.register(r'groups', GroupViewSet)
#router.register(r'api/v1/status', views.MyRESTView)


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/status/?$', MyRESTView.as_view(), name="server_status"),
    url(r'^api/v1/information/?$', BTCGetInfoView.as_view(), name="BTC_Get_Information"),
    # url(r'^api/v1/address/$', BTCGetNewAddress.as_view(), name="BTC_Create_New_Address"),
    url(r'^api/v1/address/?$', CreateNewAddresses.as_view(), name="BTC_Create_New_Address"),
    # url(r'^api/v1/receive/$', BTCCheckAddressReceive.as_view(), name="BTC_Check_Address_For_Bitcoin_Receiving"),
    url(r'^api/v1/receive/?$', CheckMultiAddressesReceive.as_view(), name="BTC_Check_Address_For_Bitcoin_Receiving"),
    url(r'^api/v1/balance/?$', GetBalanceView.as_view(), name="BTC_GET_BALANCE_FOR_A_ADDRESS"),
    url(r'^api/v1/send/?$', SendCurrencyView.as_view(), name="BTC_SEND_To_A_ADDRESS"),
    url(r'^api/v1/wallet/balance/?$', CheckWalletsBalance.as_view(), name="Check_Wallets_Balance"),
    url(r'^api/v1/transfer/?$', TransferCurrencyByUsingSendTaoAddress.as_view(),
        name="Transfer_currency_to_a_fixed_address"),
    url(r'^api/v1/sendmany/?$', BTCSendManyView.as_view(), name="BTC Send Many"),
    # ... your url patterns
]

'''urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'btcxblockchainapi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/status/?$', MyRESTView.as_view(), name="server_status"),
    url(r'^api/v1/information/?$', BTCGetInfoView.as_view(), name="BTC_Get_Information"),
    #url(r'^api/v1/address/$', BTCGetNewAddress.as_view(), name="BTC_Create_New_Address"),
    url(r'^api/v1/address/?$', CreateNewAddresses.as_view(), name="BTC_Create_New_Address"),
    #url(r'^api/v1/receive/$', BTCCheckAddressReceive.as_view(), name="BTC_Check_Address_For_Bitcoin_Receiving"),
    url(r'^api/v1/receive/?$', CheckMultiAddressesReceive.as_view(), name="BTC_Check_Address_For_Bitcoin_Receiving"),
    url(r'^api/v1/balance/?$', GetBalanceView.as_view(), name="BTC_GET_BALANCE_FOR_A_ADDRESS"),
    url(r'^api/v1/send/?$', SendCurrencyView.as_view(), name="BTC_SEND_To_A_ADDRESS"),
    url(r'^api/v1/wallet/balance/?$', CheckWalletsBalance.as_view(), name="Check_Wallets_Balance"),
    url(r'^api/v1/transfer/?$', TransferCurrencyByUsingSendTaoAddress.as_view(), name="Transfer_currency_to_a_fixed_address"),
    url(r'^api/v1/sendmany/?$', BTCSendManyView.as_view(), name="BTC Send Many"),
    #url(r'^ws/foo$', WalletNotificationView.as_view(), name="Wallets_Balance_notification"),

    #url(r'^api/v1/receive/(?P<txid>[A-Za-z0-9]+)/$', CheckTransaction.as_view(), name = "Check a receive transaction"),
    #url(r'^api/v1/receive/(?P<address>[A-Za-z0-9]+)/$', CheckAmountReceived.as_view(), name = "Check amount received from a address"),
    )'''

#urlpatterns = format_suffix_patterns(urlpatterns)
