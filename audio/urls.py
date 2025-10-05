from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path('admin/', admin.site.urls),
    # path('', include('audio.urls')),
    # path("submit-payment/", views.submit_manual_payment, name="submit_payment"),
    # path("payment-status/", views.payment_status, name="payment_status"),
    path("upload_audio/", views.upload_and_separate, name="upload_audio"),
    # path("audio-outputs/", views.audio_outputs, name="audio_outputs"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)