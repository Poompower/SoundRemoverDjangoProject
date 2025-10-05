from django.contrib import admin
from .models import ManualPayment, UserProfile, AudioFile, OutputFile

@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "order_number", "amount", "status", "created_at"]
    actions = ["approve_payment"]

    def approve_payment(self, request, queryset):
        for payment in queryset:
            if payment.status != "approved":
                payment.status = "approved"
                payment.save()
                profile, _ = UserProfile.objects.get_or_create(user=payment.user)
                profile.tickets += 50
                if profile.tickets > 50:
                    profile.tickets = 50
                profile.generate_qr()
                profile.save()
        self.message_user(request, "Selected payments approved and tickets added")
    approve_payment.short_description = "Approve selected payments and add 50 tickets"
