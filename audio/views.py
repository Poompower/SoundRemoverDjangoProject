from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
import os
from django.conf import settings
from django.db.models import *
from django.views import View
import subprocess
from pathlib import Path 
def index(request):
    return render(request, 'index.html')
def separate_audio(input_path, output_path):
    subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{input_path.parent}:/input",
        "deezer/spleeter:latest",
        "separate",
        "-i", f"/input/{input_path.name}",
        "-p", "spleeter:2stems",
        "-o", f"/input/{output_path.name}"
    ])
def upload_and_separate(request):
    if request.method == "POST":
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.save(commit=False)
            audio_file.save()

            input_path = Path(audio_file.original_file.path)
            output_dir = input_path.parent / f"separated_{audio_file.id}"
            output_dir.mkdir(parents=True, exist_ok=True)

            try:
                separate_audio(input_path, output_dir)

                for stem in ["vocals", "accompaniment"]:
                    stem_file = output_dir / input_path.stem / f"{stem}.wav"
                    if stem_file.exists():
                        OutputFile.objects.create(
                            audio=audio_file,
                            stem_type=stem,
                            file=f"uploads/originals/separated_{audio_file.id}/{input_path.stem}/{stem}.wav"
                        )
                audio_file.status = "processed"
                audio_file.save()
            except Exception as e:
                audio_file.status = "failed"
                audio_file.save()
                print("Error:", e)

            return redirect("audio_result", audio_id=audio_file.id)
    else:
        form = UploadAudioForm()

    return render(request, "upload_audio.html", {"form": form})
# @login_required
# def submit_manual_payment(request):
#     if request.method == "POST":
#         form = ManualPaymentForm(request.POST, request.FILES)
#         if form.is_valid():
#             payment = form.save(commit=False)
#             payment.user = request.user
#             payment.save()
#             return redirect("payment_status")
#     else:
#         form = ManualPaymentForm()
#     return render(request, "submit_payment.html", {"form": form})

# @login_required
# def payment_status(request):
#     payments = request.user.manualpayment_set.all().order_by("-created_at")
#     return render(request, "payment_status.html", {"payments": payments})

# @login_required
# def upload_and_separate(request):
#     user_profile = UserProfile.objects.get(user=request.user)

#     if request.method == "POST":
#         form = UploadAudioForm(request.POST, request.FILES)
#         if form.is_valid():
#             audio_file = form.save(commit=False)
#             audio_file.owner = user_profile
#             audio_file.save()

#             # run spleeter
#             input_path = Path(audio_file.original_file.path)
#             output_dir = input_path.parent / f"separated_{audio_file.id}"
#             output_dir.mkdir(parents=True, exist_ok=True)

#             try:
#                 separate_audio(input_path, output_dir)

#                 for stem in ["vocals", "accompaniment"]:
#                     stem_file = output_dir / input_path.stem / f"{stem}.wav"
#                     if stem_file.exists():
#                         OutputFile.objects.create(
#                             audio=audio_file,
#                             stem_type=stem,
#                             file=f"uploads/originals/separated_{audio_file.id}/{input_path.stem}/{stem}.wav"
#                         )
#                 audio_file.status = "processed"
#                 audio_file.save()
#             except Exception as e:
#                 audio_file.status = "failed"
#                 audio_file.save()
#                 print("Error:", e)

#             return redirect("audio_result", audio_id=audio_file.id)
#     else:
#         form = UploadAudioForm()

#     return render(request, "seperate_audio.html", {"form": form})


# @login_required
# def audio_outputs(request):
#     files = AudioFile.objects.filter(owner=request.user).order_by("-uploaded_at")
#     return render(request, "audio_outputs.html", {"files": files})
