from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import datetime
from django.contrib.auth.decorators import login_required  # Tambahkan baris ini
from django.core.exceptions import PermissionDenied        # Tambahkan baris ini

from main.models import Experience, Education
from main.forms import ExperienceForm, EducationForm

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Jonathan Sebastian Sindhu",
        "npm": "2506619650",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Motivated Computer Science student with strong academic achievements and experience in competitive programming. Skilled in algorithms, problem-solving, and C++ programming, with proven accomplishments in national informatics competitions. Committed to excellence in Computer Science, demonstrating both technical expertise and leadership through tutoring and training activities."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)

def show_experience(request):
    json_response = get_experiences_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    
    experiences = [experience.object for experience in experiences]
    
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Jonathan Sebastian Sindhu", 
        "experience_list": experiences,
        "title_query": title_query,
    }
    
    return render(request, "experience.html", context)

def show_education(request):
    json_response = get_educations_json(request)

    educations = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    
    educations = [education.object for education in educations]
    
    institution_name_query = request.GET.get("institution_name", "").strip()

    is_editor = is_editor_user(request.user)

    context = {
        "name": "Jonathan Sebastian Sindhu", 
        "education_list": educations,
        "institution_name_query": institution_name_query,
        "is_editor": is_editor,
    }

    return render(request, "education.html", context)

@login_required(login_url="/login/")  # Tambahkan baris ini
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
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
    experiences_json = serializers.serialize(
        "json", experiences, use_natural_foreign_keys=True
    )
    return HttpResponse(experiences_json, content_type="application/json")

@login_required(login_url="/login/")  # Tambahkan baris ini
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted successfully!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

@login_required(login_url="/login/")  # Tambahkan baris ini
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New education added!")
        return redirect("main:show_education")

    context = {
        "name": "Jonathan Sebastian Sindhu",
        "form": form,
        "is_update": False,
    }
    return render(request, "education_form.html", context)

def get_educations_json(request):
    institution_query = request.GET.get("institution_name", "").strip()
    
    educations = Education.objects.all()

    if institution_query:
        educations = educations.filter(institution_name__icontains=institution_query)

    education_json = serializers.serialize(
        "json", educations, use_natural_foreign_keys=True
    )
    return HttpResponse(education_json, content_type="application/json")

@login_required(login_url="/login/")  # Tambahkan baris ini
def delete_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education deleted successfully!")
        return redirect("main:show_education")

    return redirect("main:show_education")

@login_required(login_url="/login/")  # Tambahkan baris ini
def update_education(request, education_id):
    if not (request.user.is_superuser or is_editor_user(request.user)):
        raise PermissionDenied

    education = get_object_or_404(Education, id=education_id)

    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education updated successfully!")
        return redirect('main:show_education')

    context = {
        "name": "Jonathan Sebastian Sindhu",
        "form": form,
        "is_update": True,
    }
    return render(request, "education_form.html", context)

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Jonathan Sebastian Sindhu",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Jonathan Sebastian Sindhu",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)

    return redirect("main:show_experience")

@login_required(login_url="/login/")
def toggle_education_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        if request.user in education.starred_by.all():
            education.starred_by.remove(request.user)
        else:
            education.starred_by.add(request.user)

    return redirect("main:show_education")

def is_editor_user(user):
    return user.is_authenticated and user.groups.filter(name='Editor').exists()

@login_required(login_url='/login/')
def show_favorites(request):
    # Mengambil data Education dan Experience yang di-star oleh user yang sedang login
    # Kita menggunakan order_by('-started_at') untuk menjaga urutan kronologis terbalik
    favorite_educations = Education.objects.filter(starred_by=request.user).order_by('-started_at')
    favorite_experiences = Experience.objects.filter(starred_by=request.user).order_by('-started_at')
    
    context = {
        'name': 'Jonathan Sebastian Sindhu',
        'favorite_educations': favorite_educations,
        'favorite_experiences': favorite_experiences,
    }
    
    return render(request, "favorites.html", context)