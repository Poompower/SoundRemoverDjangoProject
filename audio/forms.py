from django import forms
from .models import ManualPayment, AudioFile

class ManualPaymentForm(forms.ModelForm):
    class Meta:
        model = ManualPayment
        fields = ["order_number", "slip_image", "transfer_datetime", "amount"]
        widgets = {"transfer_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"})}


class UploadAudioForm(forms.ModelForm):
    class Meta:
        model = AudioFile
        fields = ["original_file"]
