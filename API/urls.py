from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Opslogin/',views.OpsUserLogin.as_view(),name='Opslogin'),
    path('UploadFile/',views.UploadFile.as_view(),name='UploadFile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)