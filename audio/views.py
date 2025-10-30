from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User, Group
from pathlib import Path
import subprocess
from .forms import *
from .models import *

# -------------------------------
# หน้าแรก (Index)
# -------------------------------


def index(request):
    return render(request, "index.html", {
        "login_form": LoginForm(),
        "register_form": RegisterForm(),
    })


# -------------------------------
# Login
# -------------------------------
def signin(request):
    register_form = RegisterForm()
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print(f"✅ Login success: {user.username}")

            if user.is_staff:
                return redirect("admin_dashboard")
            else:
                return redirect("dashboard")
        else:
            #  Loginผิดrenderกลับพร้อมerror
            return render(request, "index.html", {
                "login_form": form,
                "register_form": register_form,
            })
    form = LoginForm()
    return render(request, "index.html", {
        "login_form": form,
        "register_form": register_form,
    })

# -------------------------------
# Register
# -------------------------------


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name="user")
            user.groups.add(group)
            print(f"User created: {user.username}")

            UserProfile.objects.create(user=user)
            login(request, user)
            print("🎫 UserProfile created and user logged in")
            return redirect("dashboard")
        else:
            print("Register form invalid:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            login_form = LoginForm()
            return render(request, "index.html", {
                "login_form": login_form,
                "register_form": form,  # ส่งฟอร์มที่มี error กลับ
            })
    else:
        form = LoginForm()
        register_form = RegisterForm()

    return redirect("index")


# -------------------------------
# Dashboard
# -------------------------------
@login_required
@permission_required('audio.view_audiofile', raise_exception=True)
def dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    audio_files = profile.audio_files.all()
    context = {
        "profile": profile,
        "audio_files": audio_files,
    }
    return render(request, "dashboard.html", context)


# -------------------------------
# Logout
# -------------------------------
def signout(request):
    logout(request)
    return redirect("index")

# -------------------------------
# Edit Profile
# -------------------------------


@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = EditProfileForm(instance=user)

    return render(request, "edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            logout(request)
            return redirect("index")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "change_password.html", {"form": form})
# -------------------------------
# ฟังก์ชันแยกเสียง (Spleeter)
# -------------------------------


def separate_audio(input_path, output_path):
    try:
        result = subprocess.run([
            "docker", "run", "--rm",  # Docker รัน container ลบ container ทิ้งอัตโนมัติหลังเสร็จงาน
            # <โฟลเดอร์บนเครื่องจริง>:<โฟลเดอร์ใน container>
            "-v", f"{input_path.parent}:/input",
            "researchdeezer/spleeter",  # ชื่อ Docker image ที่ใช้
            "separate",  # คำสั่งภายใน container ที่ใช้แยกเสียง
            "-i", f"/input/{input_path.name}",
            "-p", "spleeter:2stems",
            "-o", f"/input/{output_path.name}"
        ], capture_output=True, text=True, encoding="utf-8", errors="ignore")

        if result.returncode != 0:
            print("❌ Docker Spleeter failed:")
            print(result.stderr)
            return False  # ถ้า result.returncode ไม่เท่ากับ 0 → แปลว่าการรัน Docker ล้มเหลว พิมพ์ error ออก console แล้ว return False
        return True
    except FileNotFoundError:
        # Docker ไม่ได้ติดตั้งหรือเปิดอยู่
        print("❌ Docker not found or not running")
        return False
    except Exception as e:
        # ดัก error อื่น ๆ เช่น Path ไม่ถูก, Permission denied
        print("❌ Error running Spleeter:", e)
        return False
# -------------------------------
# Upload + Separate
# -------------------------------


@login_required
@permission_required('audio.add_audiofile', raise_exception=True)
def upload_audio(request):
    if request.method == "POST":
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = UserProfile.objects.get(user=request.user)

            # ตรวจสอบ ticket ของผู้ใช้
            if user_profile.tickets <= 0:
                return redirect("dashboard")

            user_profile.tickets -= 1
            user_profile.save()

            audio_file = form.save(commit=False)
            audio_file.owner = user_profile
            audio_file.status = "pending"
            audio_file.save()  # addไฟล์เข้าระบบ จะได้idมา
            # เตรียมโฟลเดอร์สำหรับเก็บไฟล์แยกเสียง
            input_path = Path(audio_file.original_file.path)
            # user_dir = Path("media/user_poompower")
            user_dir = input_path.parent
            output_dir = user_dir / f"separated_{audio_file.id}"
            # Path("media/user_poompower/separated_7").mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)

            try:
                success = separate_audio(input_path, output_dir)  # return true false

                if not success:
                    audio_file.status = "failed"
                else:
                    for stem in ["vocals", "accompaniment"]:
                        stem_file = output_dir / \
                            input_path.stem / f"{stem}.wav"
                        # media/user_poompower/separated_7/my_song/vocals.wav
                        # media/user_poompower/separated_7/my_song/accompaniment.wav
                        if stem_file.exists():
                            OutputFile.objects.create(
                                audio=audio_file,
                                stem_type=stem,
                                file=f"user_{request.user.username}/separated_{audio_file.id}/{input_path.stem}/{stem}.wav"
                            )
                    audio_file.status = "processed"
            except Exception as e:
                audio_file.status = "failed"
                print("Error:", e)

            audio_file.save()  # อัปเดตหลังจากแยกเสียงเสร็จ
            return redirect("dashboard")
    else:
        form = UploadAudioForm()
    return render(request, "upload_audio.html", {"form": form})

# -------------------------------
# View Audio
# -------------------------------


@login_required
@permission_required('audio.view_audiofile', raise_exception=True)
def audio_detail(request, audio_id):
    audio = AudioFile.objects.get(id=audio_id)
    outputs = OutputFile.objects.filter(audio=audio)
    tags = Tag.objects.all()

    is_owner = (audio.owner.user == request.user)

    if request.method == "POST":
        if is_owner:
            selected_tags = request.POST.getlist(
                "tags")  # ดึงค่าจาก select multiple
            # Django ลบแท็กเก่าและเพิ่มแท็กใหม่ให้อัตโนมัติ
            audio.tags.set(selected_tags)
            audio.save()
        return redirect("dashboard")

    return render(request, "audio_detail.html", {
        "audio": audio,
        "outputs": outputs,
        "tags": tags,
        "is_owner": is_owner,
    })

# -------------------------------
# Delete Audio
# -------------------------------


@login_required
@permission_required('audio.delete_outputfile', raise_exception=True)
def delete_audio(request, audio_id):
    audio = AudioFile.objects.get(id=audio_id, owner__user=request.user)
    if request.method == "POST":
        # ลบ OutputFile ทั้งหมดที่เกี่ยวข้อง
        OutputFile.objects.filter(audio=audio).delete()
        # ลบไฟล์ต้นฉบับจากฐานข้อมูล
        audio.delete()
        return redirect("dashboard")
    return redirect("audio_detail", audio_id=audio.id)


@login_required
@permission_required('audio.add_manualpayment', raise_exception=True)
def buy_ticket(request):
    if request.method == "POST":
        form = ManualPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.status = "pending"
            payment.save()
            return redirect("ticket_dashboard")
    else:
        form = ManualPaymentForm()

    return render(request, "buy_ticket.html", {"form": form})


@login_required
@permission_required('audio.view_manualpayment', raise_exception=True)
def ticket_dashboard(request):
    # ดึงประวัติการชำระเงินของ user คนปัจจุบัน
    payments = ManualPayment.objects.filter(
        user=request.user).order_by('created_at')
    return render(request, "ticket_dashboard.html", {"payments": payments})
# -------------------------------
# Admin Dashboard (ดูรายการ ManualPayment ทั้งหมด)
# -------------------------------


@login_required
@permission_required('audio.change_manualpayment', raise_exception=True)
def admin_dashboard(request):
    payments = ManualPayment.objects.all().order_by('-created_at')
    return render(request, "admin_dashboard.html", {"payments": payments})


@login_required
@permission_required('audio.change_manualpayment', raise_exception=True)
def approve_payment(request, payment_id):
    if request.method == "POST":
        payment = ManualPayment.objects.get(id=payment_id)
        payment.status = "approved"
        payment.save()

        # ✅ เพิ่ม Ticket ให้ user
        profile, _ = UserProfile.objects.get_or_create(user=payment.user)
        profile.tickets += 50
        profile.save()
    return redirect("admin_dashboard")


@login_required
@permission_required('audio.change_manualpayment', raise_exception=True)
def reject_payment(request, payment_id):
    if request.method == "POST":
        payment = ManualPayment.objects.get(id=payment_id)
        payment.status = "rejected"
        payment.save()
    return redirect("admin_dashboard")


@login_required
@permission_required('audio.view_userprofile', raise_exception=True)
def viewUser(request):
    users = UserProfile.objects.all().filter(user__is_staff=False) 
    return render(request, "userprofile.html", {"users": users})


@login_required
@permission_required('audio.view_audiofile', raise_exception=True)
def admin_view_history(request, user_id):
    profile = UserProfile.objects.get(user__id=user_id)
    audio_files = profile.audio_files.all()

    context = {
        "profile": profile,
        "audio_files": audio_files,
    }
    return render(request, "dashboard.html", context)


@login_required
@permission_required('audio.view_outputfile', raise_exception=True)
def admin_view_audio(request, audio_id, user_id):
    audio = AudioFile.objects.get(id=audio_id)
    outputs = OutputFile.objects.filter(audio=audio)
    tags = Tag.objects.all()

    return render(request, "audio_detail.html", {
        "audio": audio,
        "outputs": outputs,
        "tags": tags,
    })


def view_all_tags(request):
    tags = Tag.objects.all().order_by("created_at")
    return render(request, "tag.html", {"tags": tags})


@login_required
@permission_required('audio.add_tag', raise_exception=True)
def create_tag(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            # ตรวจชื่อซ้ำ
            if not Tag.objects.filter(name__iexact=name).exists():
                Tag.objects.create(name=name, created_by=request.user)
            return redirect("view_all_tags")
        else:
            return redirect("create_tag")
    return render(request, "create_tag.html")
# -------------------------------
# Change Tag
# -------------------------------


@login_required
@permission_required('audio.change_tag', raise_exception=True)
def change_tag(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    if request.method == "POST":
        new_name = request.POST.get("name")
        if new_name:
            if not Tag.objects.filter(name__iexact=new_name).exclude(id=tag.id).exists():
                tag.name = new_name
                tag.save()
            return redirect("view_all_tags")
    return render(request, "change_tag.html", {"tag": tag})


# -------------------------------
# Delete Tag
# -------------------------------
@login_required
@permission_required('audio.delete_tag', raise_exception=True)
def delete_tag(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    if request.method == "POST":
        tag.delete()
    return redirect("view_all_tags")
