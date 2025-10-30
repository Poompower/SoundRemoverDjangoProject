from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    path("login/", views.signin, name="login"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.signout, name="logout"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
    path("upload_audio/", views.upload_audio, name="upload_audio"),
    path("audio/<int:audio_id>/", views.audio_detail, name="audio_detail"),
    path("audio/<int:audio_id>/delete/",
         views.delete_audio, name="delete_audio"),
    path("buy-ticket/", views.buy_ticket, name="buy_ticket"),
    path("ticket-dashboard/", views.ticket_dashboard, name="ticket_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("view-user/", views.viewUser, name="viewUser"),
    path("view-user/<int:user_id>", views.admin_view_history,
         name="admin_view_history"),
    path("view-user/<int:user_id>/audio/<int:audio_id>",
         views.admin_view_audio, name="admin_view_audio"),
    path("payment/<int:payment_id>/approve/",
         views.approve_payment, name="approve_payment"),
    path("payment/<int:payment_id>/reject/",
         views.reject_payment, name="reject_payment"),
    path("tags/", views.view_all_tags, name="view_all_tags"),
    path("tags/create/", views.create_tag, name="create_tag"),
    path("tags/<int:tag_id>/change/", views.change_tag, name="change_tag"),
    path("tags/<int:tag_id>/delete/", views.delete_tag, name="delete_tag"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
