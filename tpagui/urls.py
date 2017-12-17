"""tpagui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from tpa.views import newChoiceAutocomplete
from tpa.views import home, about, contact
from django.conf import settings
from tastypie.api import Api
from tpa.api.resources import QuestionResource

ques_resource = QuestionResource()

urlpatterns = [
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^tpa/', include('tpa.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', home),
    url(r'^about/$', about),
    url(r'^contact/$', contact),
    url(r'^newchoice-autocomplete/$',
        newChoiceAutocomplete.as_view(),
        name='newchoice-autocomplete',
    ),
    url(r'^api/', include(ques_resource.urls)),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns