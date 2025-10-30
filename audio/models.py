from django.db import models
from django.contrib.auth.models import User
from io import BytesIO
from django.core.files.base import ContentFile

# ----------------------------
# User Profile
# ----------------------------


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tickets = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} UserProfile"

# ----------------------------
# Manual Payment (PromptPay / Slip)
# ----------------------------


class ManualPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    slip_image = models.ImageField(upload_to="payment_slips/")
    transfer_datetime = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ("pending", "กำลังตรวจสอบ"),
        ("approved", "ยืนยันแล้ว"),
        ("rejected", "ปฏิเสธ"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_status_display()})"

# ----------------------------
# Sound Remover Models
# ----------------------------

# แท็กสำหรับจัดหมวดหมู่ไฟล์เสียง


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tags")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

def user_audio_path(instance, filename):
    """
    เก็บไฟล์เสียงลงในโฟลเดอร์ของ user เช่น:
    uploads/originals/user_5/filename.mp3
    """
    username = instance.owner.user.username
    return f"user_{username}/{filename}"
def user_output_path(instance, filename):
    """
    เก็บไฟล์ผลลัพธ์ไว้ในโฟลเดอร์ของ username เช่น:
    media/<username>/outputs/<filename>
    """
    username = instance.audio.owner.user.username
    return f"user_{username}/outputs/{filename}"
# ไฟล์เสียงต้นฉบับที่ผู้ใช้อัปโหลด


class AudioFile(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )

    owner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="audio_files")  # one-to-many
    original_file = models.FileField(upload_to=user_audio_path)
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
    file = models.FileField(upload_to=user_output_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Output {self.stem_type} for AudioFile {self.audio.id}"
