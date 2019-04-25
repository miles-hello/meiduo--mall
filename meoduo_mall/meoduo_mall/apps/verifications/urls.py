from django.conf.urls import url
from . import views

urlpatterns=[

    url('^image_codes/(?P<uuid>.+)/$',views.Imagecodeview.as_view())
]