from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from main.models import Experience, Education
from main.forms import ExperienceForm, EducationForm

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

    context = {
        "name": "Jonathan Sebastian Sindhu", 
        "education_list": educations,
        "institution_name_query": institution_name_query,
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
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted successfully!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

def create_education(request):
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

    education_json = serializers.serialize("json", educations)
    return HttpResponse(education_json, content_type="application/json")

def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education deleted successfully!")
        return redirect("main:show_education")

    return redirect("main:show_education")

def update_education(request, education_id):
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