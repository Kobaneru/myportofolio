from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import datetime
from django.contrib.auth.decorators import login_required  # Tambahkan baris ini
from django.core.exceptions import PermissionDenied        # Tambahkan baris ini
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Jonathan Sebastian Sindhu", 
        "title_query": title_query,
        # Form kosong dipakai oleh modal "Add Experience" (submit via AJAX)
        "form": ExperienceForm(),
    }

    return render(request, "experience.html", context)


def show_education(request):
    institution_name_query = request.GET.get("institution_name", "").strip()

    is_editor = is_editor_user(request.user)

    context = {
        "name": "Jonathan Sebastian Sindhu", 
        "institution_name_query": institution_name_query,
        # Alias agar template dapat memakai {{ institution_query }} pada empty state
        "institution_query": institution_name_query,
        "is_editor": is_editor,
        "form": EducationForm(),
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
    experiences = Experience.objects.prefetch_related('starred_by').all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for experience in experiences:
        starred_users = experience.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(experience.id),
            "fields": {
                "title": experience.title,
                "description": experience.description,
                "category": experience.category,
                "thumbnail": experience.thumbnail,
                "started_at": experience.started_at,
                "ended_at": experience.ended_at,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })
    
    return JsonResponse(data, safe=False)

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


def _serialize_experience(request, experience):
    """Membantu mengubah satu objek Experience menjadi dict siap-JSON."""
    return {
        "id": str(experience.id),
        "title": experience.title,
        "category": experience.get_category_display(),
        "thumbnail": experience.thumbnail or "",
        "is_ongoing": experience.is_ongoing,
        "started_at": experience.started_at.strftime("%B %Y") if experience.started_at else "",
        "ended_at": experience.ended_at.strftime("%B %Y") if experience.ended_at else "",
        "description": experience.description,
        "star_html": render_to_string(
            "components/experience_star.html",
            {"experience": experience},
            request=request,
        ),
        "delete_html": "",
        "edit_html": "",
    }


def show_json(request):
    """Menampilkan seluruh data Experience dalam format JSON."""
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.prefetch_related("starred_by").all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    data = [_serialize_experience(request, experience) for experience in experiences]

    if request.user.is_superuser:
        for item, experience in zip(data, experiences):
            item["delete_html"] = render_to_string(
                "components/experience_delete_modal.html",
                {"experience": experience},
                request=request,
            )
            item["edit_html"] = render_to_string(
                "components/experience_edit_modal.html",
                {"experience": experience, "form": ExperienceForm(instance=experience)},
                request=request,
            )

    return JsonResponse(data, safe=False)


def show_json_by_id(request, id):
    """Menampilkan satu data Experience berdasarkan id dalam format JSON."""
    experience = Experience.objects.filter(pk=id).first()

    if experience is None:
        return JsonResponse(
            {"status": "error", "message": "Experience tidak ditemukan"},
            status=404,
        )

    return JsonResponse(_serialize_experience(request, experience))


@csrf_exempt
@require_POST
def create_experience_ajax(request):
    """Menambahkan Experience baru melalui AJAX."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse(
            {"status": "error", "message": "Hanya admin yang boleh menambah data"},
            status=403,
        )

    form = ExperienceForm(request.POST)

    if form.is_valid():
        form.save()
        return JsonResponse(
            {"status": "success", "message": "New experience added!"},
            status=201,
        )

    return JsonResponse(
        {"status": "error", "message": "Data tidak valid", "errors": form.errors},
        status=400,
    )


@csrf_exempt
@require_POST
def delete_experience_ajax(request, id):
    """Menghapus Experience melalui AJAX."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse(
            {"status": "error", "message": "Hanya admin yang boleh menghapus data"},
            status=403,
        )

    experience = Experience.objects.filter(pk=id).first()

    if experience is None:
        return JsonResponse(
            {"status": "error", "message": "Experience tidak ditemukan"},
            status=404,
        )

    experience.delete()
    return JsonResponse(
        {"status": "success", "message": "Experience berhasil dihapus"}
    )


@csrf_exempt
@require_POST
def update_experience_ajax(request, id):
    """Memperbarui Experience melalui AJAX."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse(
            {"status": "error", "message": "Hanya admin yang boleh mengubah data"},
            status=403,
        )

    experience = Experience.objects.filter(pk=id).first()

    if experience is None:
        return JsonResponse(
            {"status": "error", "message": "Experience tidak ditemukan"},
            status=404,
        )

    form = ExperienceForm(request.POST, instance=experience)

    if form.is_valid():
        form.save()
        return JsonResponse(
            {"status": "success", "message": "Experience berhasil diperbarui!"}
        )

    return JsonResponse(
        {"status": "error", "message": "Data tidak valid", "errors": form.errors},
        status=400,
    )


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
    educations = Education.objects.prefetch_related('starred_by').all()

    if institution_query:
        educations = educations.filter(institution_name__icontains=institution_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for education in educations:
        starred_users = education.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(education.id),
            "fields": {
                "institution_name": education.institution_name,
                "degree": education.degree,
                "description": education.description,
                "started_at": education.started_at,
                "ended_at": education.ended_at,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
                "edit_html": render_to_string(
                    "components/education_edit_modal.html",
                    {
                        "education": education,
                        "form": EducationForm(instance=education),
                    },
                    request=request,
                ) if request.user.is_superuser or is_editor_user(request.user) else "",
                "delete_html": render_to_string(
                    "components/education_delete_modal.html",
                    {"education": education},
                    request=request,
                ) if request.user.is_superuser else "",
            }
        })

    return JsonResponse(data, safe=False)


@require_POST
def create_education_ajax(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan education."},
            status=403,
        )

    form = EducationForm(request.POST)
    if form.is_valid():
        education = form.save()
        return JsonResponse(
            {"message": "Education berhasil ditambahkan.", "pk": str(education.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_POST
def update_education_ajax(request, education_id):
    if not request.user.is_authenticated or not (
        request.user.is_superuser or is_editor_user(request.user)
    ):
        return JsonResponse(
            {"message": "Hanya Superuser atau Editor yang dapat mengubah education."},
            status=403,
        )

    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST, instance=education)
    if form.is_valid():
        form.save()
        return JsonResponse(
            {"message": "Education berhasil diperbarui.", "pk": str(education.id)},
            status=200,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

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