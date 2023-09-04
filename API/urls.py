from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Opslogin/',views.OpsUserLogin.as_view(),name='Opslogin'),
    path('UploadFile/',views.UploadFile.as_view(),name='UploadFile'),
    path('ClientSignup/',views.ClientSignup.as_view(),name='ClientSignup'),
    path('PasswordTokenCheck/<uidb64>/<token>/',views.PasswordTokenCheck.as_view(),name='PasswordTokenCheck-confirm'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)