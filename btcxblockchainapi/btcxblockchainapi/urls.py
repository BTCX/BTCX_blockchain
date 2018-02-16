#from django.conf.urls import patterns, include, url
from django.conf.urls import include, url
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from btcrpc.view.check_wallets_balance import CheckWalletsBalance
from btcrpc.view.send_many_view import BTCSendManyView
from btcrpc.view.transfer_using_sendtoaddress import TransferCurrencyByUsingSendTaoAddress
from btcrpc.views import *
from quickstart.views import *
from btcrpc.view.addresses import *
from btcrpc.view.check_multi_receives import *


from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users',  UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/address/?$', CreateNewAddresses.as_view(), name="BTC_Create_New_Address"),
    url(r'^api/v1/receive/?$', CheckMultiAddressesReceive.as_view(), name="BTC_Check_Address_For_Bitcoin_Receiving"),
    url(r'^api/v1/wallet/balance/?$', CheckWalletsBalance.as_view(), name="Check_Wallets_Balance"),
    url(r'^api/v1/transfer/?$', TransferCurrencyByUsingSendTaoAddress.as_view(),
        name="Transfer_currency_to_a_fixed_address"),
    url(r'^api/v1/sendmany/?$', BTCSendManyView.as_view(), name="BTC Send Many"),
    # ... your url patterns
]
