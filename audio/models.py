from django.db import models
from django.contrib.auth.models import User
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode

# ----------------------------
# User & Role / Profile
# ----------------------------


class Role(models.Model):
    name = models.CharField(max_length=50)  # 'User', 'Admin'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role, related_name="users")  # many-to-many
    tickets = models.PositiveIntegerField(default=0)
    qr_code = models.ImageField(
        upload_to="user_qrcodes/", blank=True, null=True)

    def generate_qr(self, payload=None):
        if not payload:
            payload = f"user:{self.user.pk}:tickets:{self.tickets}"
        img = qrcode.make(payload)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        file_name = f"user_{self.user.pk}_qr.png"
        self.qr_code.save(file_name, ContentFile(
            buffer.getvalue()), save=False)
        buffer.close()
        self.save()

    def __str__(self):
        return f"{self.user.username} UserProfile"

# ----------------------------
# Manual Payment (PromptPay / Slip)
# ----------------------------


class ManualPayment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payments")  # one-to-many
    order_number = models.CharField(max_length=50)
    slip_image = models.ImageField(upload_to="payment_slips/")
    transfer_datetime = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ("pending", "กำลังตรวจสอบ"),
        ("approved", "ยืนยันแล้ว"),
        ("rejected", "ปฏิเสธ"),
    ]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_number} - {self.user.username}"

# ----------------------------
# Sound Remover Models
# ----------------------------

# แท็กสำหรับจัดหมวดหมู่ไฟล์เสียง


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# ไฟล์เสียงต้นฉบับที่ผู้ใช้อัปโหลด


class AudioFile(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )

    owner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="audio_files")  # one-to-many
    original_file = models.FileField(upload_to='uploads/originals/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="audio_files")  # many-to-many

    def __str__(self):
        return f"AudioFile {self.id} by {self.owner.user.username}"

# ไฟล์ที่ผ่านการประมวลผลแล้ว (ผลลัพธ์จาก Spleeter)


class OutputFile(models.Model):
    STEM_CHOICES = (
        ('vocals', 'Vocals'),
        ('accompaniment', 'Accompaniment'),
    )

    audio = models.ForeignKey(
        AudioFile, on_delete=models.CASCADE, related_name="outputs")  # one-to-many
    stem_type = models.CharField(max_length=30, choices=STEM_CHOICES)
    file = models.FileField(upload_to='uploads/outputs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Output {self.stem_type} for AudioFile {self.audio.id}"
