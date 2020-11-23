from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers
from btcrpc.view.check_wallets_balance import CheckWalletsBalance
from btcrpc.view.check_unconfirmed_balance import CheckUnconfirmedBalance
from btcrpc.view.send_many_view import BTCSendManyView
from btcrpc.view.transfer_using_sendtoaddress import (
    TransferCurrencyByUsingSendTaoAddress)
from btcrpc.view.get_transaction import GetTransaction
from btcrpc.view.bump_fee import BumpFee
from btcrpc.view.estimate_smart_fee import EstimateSmartFee
from quickstart.views import (UserViewSet, GroupViewSet)
from btcrpc.view.addresses import CreateNewAddresses
from btcrpc.view.check_multi_receives import CheckMultiAddressesReceive
from btcrpc.view.validate_address import ValidateAddress

from django.contrib import admin
admin.autodiscover()


router = routers.DefaultRouter()
router.register(r'users',  UserViewSet)
router.register(r'groups', GroupViewSet)

api_python_root = '^api/v1/'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/address/?$', CreateNewAddresses.as_view()),
    url(r'^api/v1/validate/?$', ValidateAddress.as_view()),
    url(r'^api/v1/receive/?$', CheckMultiAddressesReceive.as_view()),
    url(r'^api/v1/wallet/balance/?$', CheckWalletsBalance.as_view()),
    url(r'^api/v1/wallet/unconfirmedbalance/?$', CheckUnconfirmedBalance.as_view()),
    url(r'^api/v1/transfer/?$', TransferCurrencyByUsingSendTaoAddress.as_view()),
    url(r'^api/v1/sendmany/?$', BTCSendManyView.as_view()),
    url(r'^api/v1/gettransaction/?$', GetTransaction.as_view()),
    url(r'^api/v1/bumpfee/?$', BumpFee.as_view()),
    url(r'^api/v1/estimatesmartfee/?$', EstimateSmartFee.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
