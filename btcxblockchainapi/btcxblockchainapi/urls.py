from django.conf.urls import patterns, include, url
from rest_framework import routers
from quickstart import views

#from django.contrib import admin
#admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
#router.register(r'api/v1/status', views.MyRESTView)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'btcxblockchainapi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^api/v1/status/$',  'quickstart.views.MyRESTView', name="MyRESTView_test")
    url(r'^api/v1/status/$', views.MyRESTView.as_view(), name="MyRESTView_test")
 )
