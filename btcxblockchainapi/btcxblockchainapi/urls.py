from django.conf.urls import patterns, include, url
from rest_framework import routers
#from quickstart import views
#from btcrpc import views

from quickstart.views import *
from btcrpc.views import *



from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users',  UserViewSet)
router.register(r'groups', GroupViewSet)
#router.register(r'api/v1/status', views.MyRESTView)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'btcxblockchainapi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/status/$', MyRESTView.as_view(), name="server_status"),
    url(r'^api/v1/information/$', BTCGetInfoView.as_view(), name="BTC_Get_Information"),
    url(r'^api/v1/address/$', BTCGetNewAddress.as_view(), name="BTC_Create_New_Address")

    )
