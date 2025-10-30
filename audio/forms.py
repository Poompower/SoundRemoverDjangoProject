from django import forms
from .models import ManualPayment, AudioFile
from django.contrib.auth.forms import *  # AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User




class UploadAudioForm(forms.ModelForm):
    class Meta:
        model = AudioFile
        fields = ["original_file"]
    def clean_original_file(self):
        file = self.cleaned_data.get("original_file")

        if not file.name.lower().endswith(".mp3"):
            raise forms.ValidationError("ไฟล์ .mp3 เท่านั้น")

        return file

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "form-control rounded-3",
            "placeholder": "Your username",
            "autofocus": True,
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control rounded-3",
            "placeholder": "••••••••",
        })
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control rounded-3",
            "placeholder": "Firstname",
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control rounded-3",
            "placeholder": "Lastname",
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control rounded-3",
            "placeholder": "you@example.com",
        })
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name",
                  "email", "password1", "password2"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control rounded-3",
                "placeholder": "Your username",
            }),
            "password1": forms.PasswordInput(attrs={
                "class": "form-control rounded-3",
                "placeholder": "••••••••",
            }),
            "password2": forms.PasswordInput(attrs={
                "class": "form-control rounded-3",
                "placeholder": "Repeat password",
            }),
        }
    # username ซ้ำ
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("⚠️ username ซ้ำ")
        return username

    # email ซ้ำ
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("⚠️ email ซ้ำ")
        return email


class ManualPaymentForm(forms.ModelForm):
    class Meta:
        model = ManualPayment
        fields = ["slip_image", "transfer_datetime", "amount"]
        widgets = {
            "transfer_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "เช่น 100.00"}
            ),
        }
        labels = {
            "slip_image": "แนบสลิปการโอน",
            "transfer_datetime": "วันที่และเวลาโอน",
            "amount": "จำนวนเงิน (บาท)",
        }
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your username"}),
        }

    # username ซ้ำ
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("⚠️ username ซ้ำ")
        return username

    # email ซ้ำ
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("⚠️ email ซ้ำ")
        return email