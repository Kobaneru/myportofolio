from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from main.models import Experience, Education
from main.forms import ExperienceForm

def show_main(request):
    context = {
        "name": "Jonathan Sebastian Sindhu",
        "npm": "2506619650",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Motivated Computer Science student with strong academic achievements and experience in competitive programming. Skilled in algorithms, problem-solving, and C++ programming, with proven accomplishments in national informatics competitions. Committed to excellence in Computer Science, demonstrating both technical expertise and leadership through tutoring and training activities."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    # 1. Mengambil response JSON dari fungsi get_experiences_json
    json_response = get_experiences_json(request)

    # 2. Mengubah teks JSON kembali menjadi objek Python (Deserialisasi)
    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    
    # 3. Mengambil objek model aslinya dari hasil deserialisasi
    experiences = [experience.object for experience in experiences]
    
    # 4. Menangkap query pencarian dari URL (jika ada)
    title_query = request.GET.get("title", "").strip()

    # 5. Membungkus data ke dalam context untuk dikirim ke HTML
    context = {
        "name": "Jonathan Sebastian Sindhu", 
        "experience_list": experiences,
        "title_query": title_query,
    }
    
    # 6. Merender file HTML dengan membawa data context
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Jonathan Sebastian Sindhu",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)

def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New experience added!")
        return redirect("main:show_experience")

    context = {
        "name": "Jonathan Sebastian Sindhu",
        "form": form,
    }
    return render(request, "experience_form.html", context)

def get_experiences_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    # Jika ada pencarian berdasarkan judul, filter datanya
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    # Ubah data queryset menjadi format JSON
    experiences_json = serializers.serialize("json", experiences)
    return HttpResponse(experiences_json, content_type="application/json")

def delete_experience(request, experience_id):
    # Mencari data Experience berdasarkan ID, jika tidak ada akan muncul error 404
    experience = get_object_or_404(Experience, pk=experience_id)

    # Mengecek apakah aksi ini benar-benar dikirim lewat metode POST (biasanya dari form/tombol hapus)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted successfully!")
        return redirect("main:show_experience")

    # Jika ada yang iseng mengakses URL hapus secara manual lewat address bar (metode GET), 
    # langsung kembalikan ke halaman daftar experience tanpa menghapus data
    return redirect("main:show_experience")